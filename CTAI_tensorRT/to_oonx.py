import torch
import numpy as np

from CTAI_model.net import unet
import SimpleITK as sitk

device = torch.device("cuda:3" if torch.cuda.is_available() else "cpu")


def data_in_one(inputdata):
    if not inputdata.any():
        return inputdata
    inputdata = (inputdata - inputdata.min()) / (inputdata.max() - inputdata.min())
    return inputdata


def get_data(data_path):
    image = sitk.ReadImage(data_path)
    image_array = sitk.GetArrayFromImage(image)

    ROI_mask = np.zeros(shape=image_array.shape)
    ROI_mask_mini = np.zeros(shape=(1, 160, 100))
    ROI_mask_mini[0] = image_array[0][270:430, 200:300]
    ROI_mask_mini = data_in_one(ROI_mask_mini)
    ROI_mask[0][270:430, 200:300] = ROI_mask_mini[0]
    test_image = ROI_mask
    image_tensor = torch.from_numpy(ROI_mask).float().unsqueeze(1)
    return image_tensor

def init_model():
    model = unet.Unet(1, 1).to(device)
    if torch.cuda.is_available():
        model.load_state_dict(torch.load("./model.pth", map_location=device))
    else:
        model.load_state_dict(torch.load("./model.pth", map_location='cpu'))
    model.eval()
    return model


def main():
    data = get_data('20014.dcm').to(device)
    model = init_model()
    torch.onnx.export(model, data, "unet.onnx")


if __name__ == '__main__':
    main()
