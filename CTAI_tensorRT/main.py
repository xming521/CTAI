import cv2
import tensorrt as trt
import pycuda.driver as cuda
import pycuda.autoinit
import numpy as np
from PIL import Image

from CTAI_tensorRT.to_oonx import data_in_one

TRT_LOGGER = trt.Logger(trt.Logger.WARNING)

onnx_path = 'unet.onnx'
engine_path = 'model.engine'
shape = (1, 1, 512, 512)

import tensorrt as trt
import onnx
import SimpleITK as sitk


def build():
    model = onnx.load("unet.onnx")
    EXPLICIT_BATCH = 1 << (int)(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
    # Create the TensorRT engine
    with trt.Builder(TRT_LOGGER) as builder, builder.create_network(EXPLICIT_BATCH) as network, trt.OnnxParser(network,
                                                                                                               TRT_LOGGER) as parser:  # Parse the ONNX model

        parser.parse(model.SerializeToString())
        config = builder.create_builder_config()

        config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE, 1 << 25)  # 1 MiB
        config.set_flag(trt.BuilderFlag.PREFER_PRECISION_CONSTRAINTS)
        config.set_flag(trt.BuilderFlag.SPARSE_WEIGHTS)

        config.set_flag(trt.BuilderFlag.FP16)

        profile = builder.create_optimization_profile()

        profile.set_shape("input", (1, 1, 512, 512), (32, 1, 512, 512), (64, 1, 512, 512))
        config.add_optimization_profile(profile)
        serialized_engine = builder.build_serialized_network(network, config)

        # Save the TensorRT engine to disk
        with open("engine.trt", "wb") as f:
            f.write(serialized_engine)


# Simple helper data class that's a little nicer to use than a 2-tuple.
class HostDeviceMem(object):
    def __init__(self, host_mem, device_mem):
        self.host = host_mem
        self.device = device_mem

    def __str__(self):
        return "Host:\n" + str(self.host) + "\nDevice:\n" + str(self.device)

    def __repr__(self):
        return self.__str__()


def get_data(data_path):
    image = sitk.ReadImage(data_path)
    image_array = sitk.GetArrayFromImage(image)

    ROI_mask = np.zeros(shape=image_array.shape)
    ROI_mask_mini = np.zeros(shape=(1, 160, 100))
    ROI_mask_mini[0] = image_array[0][270:430, 200:300]
    ROI_mask_mini = data_in_one(ROI_mask_mini)
    ROI_mask[0][270:430, 200:300] = ROI_mask_mini[0]
    return ROI_mask


# Allocates all buffers required for an engine, i.e. host/device inputs/outputs.
def allocate_buffers(engine):
    inputs = []
    outputs = []
    bindings = []
    stream = cuda.Stream()
    input_data = get_data('20014.dcm')
    for binding in engine:
        size = trt.volume(engine.get_binding_shape(binding)) * engine.max_batch_size
        dtype = trt.nptype(engine.get_binding_dtype(binding))
        # Allocate host and device buffers
        # 申请锁页内存
        host_mem = cuda.pagelocked_empty(size, dtype)
        device_mem = cuda.mem_alloc(host_mem.nbytes)
        # Append the device buffer to device bindings.
        bindings.append(int(device_mem))
        # Append to the appropriate list.
        if engine.binding_is_input(binding):
            np.copyto(host_mem, input_data.ravel())
            inputs.append(HostDeviceMem(host_mem, device_mem))
        else:
            outputs.append(HostDeviceMem(host_mem, device_mem))
    return inputs, outputs, bindings, stream


with open("engine.trt", "rb") as f, trt.Runtime(TRT_LOGGER) as runtime:
    engine = runtime.deserialize_cuda_engine(f.read())
    with engine.create_execution_context() as context:
        # 分配输入/输出内存
        inputs, outputs, bindings, stream = allocate_buffers(engine)
        # Transfer input data to the GPU.
        [cuda.memcpy_htod_async(inp.device, inp.host, stream) for inp in inputs]
        # Run inference.
        context.execute_async(batch_size=1, bindings=bindings, stream_handle=stream.handle)
        # Transfer predictions back from the GPU.
        [cuda.memcpy_dtoh_async(out.host, out.device, stream) for out in outputs]
        # Synchronize the stream
        stream.synchronize()
        # Return only the host outputs.
        res = [out.host for out in outputs][0]
        res = res.reshape(engine.get_binding_shape(1)[1:])
        res[res >= 0.5] = 1
        res[res < 0.5] = 0
        res = res * 255
        # cv2.imwrite(f'res.png', res, (cv2.IMWRITE_PNG_COMPRESSION, 0))
