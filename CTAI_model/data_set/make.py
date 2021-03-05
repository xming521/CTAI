import os

import SimpleITK as sitk
import cv2 as cv
import numpy as np
import torch
from torch.utils import data
from torch.utils.data import random_split

train_data_path = 'E:/projects/python projects/ct_data/'
test_data_path = '../data/test/'


def get_person_files(data_path):
    # 数据结构
    # [[person_id,image,mask],[person_id,image,mask],..,]

    all = []
    dir_list = [data_path + i for i in os.listdir(data_path)]
    for dir in dir_list:
        person_id = dir.split('/')[-1]
        filename_list = []
        image_list, mask_list, = [], []
        # 所有数据跑
        temp = os.listdir(dir + '/arterial phase')
        filename_list.extend([dir + '/arterial phase/' + name for name in temp])
        for i in filename_list:
            if '.dcm' in i:
                image_list.append(i)
            if '_mask' in i:
                mask_list.append(i)

        all.append([person_id, image_list, mask_list])

    return all


def get_train_files(data_path, all, get_dice=False):
    image_list, mask_list, finish_list, id_list = [], [], [], []
    # id_list  先是病人id再是图片
    dir_list = [data_path + i for i in os.listdir(data_path)]
    filename_list = []
    for dir in dir_list:
        # 所有数据跑
        if all:
            temp = os.listdir(dir + '/arterial phase')
            filename_list.extend([dir + '/arterial phase/' + name for name in temp])
        if not all:
            filename_list.append(dir)
            # temp = os.listdir(dir)
            # filename_list.extend([dir + '/' + name for name in temp])

    for i in filename_list:
        if '.dcm' in i:
            image_list.append((i, i.split('/')[-3], i.split('/')[-1].replace('.dcm', '')))
        if '_mask' in i:
            mask_list.append(i)
        if 'finish' in i:
            finish_list.append(i)
    if get_dice:
        return image_list, mask_list, id_list
    else:
        return image_list


def data_in_one(inputdata):
    if not inputdata.any():
        return inputdata
    inputdata = (inputdata - inputdata.min()) / (inputdata.max() - inputdata.min())
    return inputdata


def get_dataset(data_path, have):
    global test_image, test_mask
    image_list, mask_list, image_data, mask_data = [], [], [], []

    image_list = get_train_files(data_path, all=True)
    for i in image_list:
        image = sitk.ReadImage(i[0])
        image_array = sitk.GetArrayFromImage(image)
        mask = i[0].replace('.dcm', '_mask.png')
        mask_array = cv.imread(mask, cv.IMREAD_GRAYSCALE)

        if have:
            if not mask_array.any():
                continue

        mask_array = data_in_one(mask_array)
        mask_tensor = torch.from_numpy(mask_array).float()
        j = i[0].split('/')[-1].replace('_mask.png', '')
        mask_data.append((j, mask_tensor))

        ROI_mask = np.zeros(shape=image_array.shape)
        ROI_mask_mini = np.zeros(shape=(1, 160, 100))
        ROI_mask_mini[0] = image_array[0][270:430, 200:300]
        ROI_mask_mini = data_in_one(ROI_mask_mini)
        ROI_mask[0][270:430, 200:300] = ROI_mask_mini[0]
        test_image = ROI_mask
        image_tensor = torch.from_numpy(ROI_mask).float()
        image_data.append((image_tensor, i[1], i[2]))

    return image_data, mask_data


def get_onlytest(data_path, have):
    global test_image, test_mask
    image_list, mask_list, image_data, mask_data = [], [], [], []

    image_list = get_train_files(data_path, all=True)
    for i in image_list:
        image = sitk.ReadImage(i[0])
        image_array = sitk.GetArrayFromImage(image)

        ROI_mask = np.zeros(shape=image_array.shape)
        ROI_mask_mini = np.zeros(shape=(1, 160, 100))
        ROI_mask_mini[0] = image_array[0][270:430, 200:300]
        ROI_mask_mini = data_in_one(ROI_mask_mini)
        ROI_mask[0][270:430, 200:300] = ROI_mask_mini[0]
        test_image = ROI_mask
        image_tensor = torch.from_numpy(ROI_mask).float()
        # print(image_tensor.shape)
        image_data.append((image_tensor, i[1], i[2]))

    return image_data


class Dataset(data.Dataset):
    def __init__(self, path, have=True, transform=None):
        imgs = get_dataset(data_path=path, have=have)
        self.imgs = imgs
        # self.transform = transform
        # self.target_transform = target_transform

    def __getitem__(self, index):
        image = self.imgs[0][index]
        mask = self.imgs[1][index]

        return image, mask

    def __len__(self):
        return len(self.imgs[0])


class testDataset(data.Dataset):
    def __init__(self, path, have=True, transform=None):
        imgs = get_onlytest(data_path=path, have=have)
        self.imgs = imgs
        # self.transform = transform
        # self.target_transform = target_transform

    def __getitem__(self, index):
        image = self.imgs[index]
        return image

    def __len__(self):
        return len(self.imgs)


def get_d1(path):
    bag = Dataset(path, have=True)
    train_size = int(0.9 * len(bag))
    test_size = len(bag) - train_size
    train_dataset, test_dataset = random_split(bag, [train_size, test_size])
    return train_dataset, test_dataset


def get_d1_local(path):
    bag = testDataset(path, have=False)
    # train_size = int(0.9 * len(bag))
    # test_size = len(bag) - train_size
    # train_dataset, test_dataset = random_split(bag, [train_size, test_size])
    return bag


if __name__ == '__main__':
    # get_train_files(train_data_path)
    # get_dataset(train_data_path,have=True)
    bag = get_d1_local()
