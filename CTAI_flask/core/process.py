import os

import SimpleITK as sitk
import cv2
import numpy as np
import torch


def data_in_one(inputdata):
    if not inputdata.any():
        return inputdata
    inputdata = (inputdata - inputdata.min()) / (inputdata.max() - inputdata.min())
    return inputdata


def pre_process(data_path):
    global test_image, test_mask
    image_list, mask_list, image_data, mask_data = [], [], [], []

    image = sitk.ReadImage(data_path)
    image_array = sitk.GetArrayFromImage(image)

    ROI_mask = np.zeros(shape=image_array.shape)
    ROI_mask_mini = np.zeros(shape=(1, 160, 100))
    ROI_mask_mini[0] = image_array[0][270:430, 200:300]
    ROI_mask_mini = data_in_one(ROI_mask_mini)
    ROI_mask[0][270:430, 200:300] = ROI_mask_mini[0]
    test_image = ROI_mask
    image_tensor = torch.from_numpy(ROI_mask).float().unsqueeze(1)
    # print(image_tensor.shape)
    image_data.append(image_tensor)
    file_name = os.path.split(data_path)[1].replace('.dcm', '')

    # 转为图片写入image文件夹

    image_array = image_array.swapaxes(0, 2)
    image_array = np.rot90(image_array, -1)
    image_array = np.fliplr(image_array).squeeze()
    # ret, image_array = cv2.threshold(image_array, 150, 255, cv2.THRESH_BINARY)
    cv2.imwrite(f'./tmp/image/{file_name}.png', image_array, (cv2.IMWRITE_PNG_COMPRESSION, 0))

    return image_data, file_name


def last_process(file_name):
    image = cv2.imread(f'./tmp/image/{file_name}.png')
    mask = cv2.imread(f'./tmp/mask/{file_name}_mask.png', 0)
    thresh, contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    draw = cv2.drawContours(image, contours, -1, (0, 255, 0), 2)
    cv2.imwrite(f'./tmp/draw/{file_name}.png', draw)
