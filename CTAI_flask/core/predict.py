import os
import sys
import cv2
import torch
import core.net.unet as net
import numpy as np

os.environ["CUDA_VISIBLE_DEVICES"] = "0"
torch.set_num_threads(4)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
torch.cuda.empty_cache()

import os

rate = 0.5


def predict(dataset,model):

    # unet = torch.load('./core/0.5unet.pkl').to(device)
    # torch.save(unet.state_dict(), "model_new.pth")

    global res, img_y, mask_arrary
    with torch.no_grad():
        x = dataset[0][0].to(device)
        file_name = dataset[1]
        y = model(x)
        img_y = torch.squeeze(y).cpu().numpy()
        img_y[img_y >= rate] = 1
        img_y[img_y < rate] = 0
        img_y = img_y * 255
        cv2.imwrite(f'./tmp/mask/{file_name}_mask.png', img_y,
                    (cv2.IMWRITE_PNG_COMPRESSION, 0))


if __name__ == '__main__':
    # 写保存模型
    # train()
    predict()
