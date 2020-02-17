import SimpleITK as sitk
import cv2
import numpy as np

from data_set.make import get_train_files

# 跑train不加第二个train
train_data_path = '../data/train/train/'


# train_data_path = '../data/CT/'


def get_roi(path):
    global w
    file_name = path.split('/')[-3] + '-' + path.split('/')[-1].replace('.dcm', '')
    image = sitk.ReadImage(path)
    image = sitk.GetArrayFromImage(image)[0, :, :]
    image[image < -300] = 0
    image[image > 300] = 0
    img_o = image.copy()
    ROI = np.zeros(image.shape, np.uint8)
    slices = [image]
    img = slices[int(len(slices) / 2)].copy()
    img = np.uint8(img)
    # kernel = np.ones((3, 3), np.uint8)
    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    # img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
    # img = cv2.dilate(img, kernel, iterations=1)

    kernel = np.ones((4, 4), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)

    # 对图像进行阈值分割
    ret, img = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY_INV)
    # 提取分割结果中的轮廓，并填充孔洞
    im2, contours, x = cv2.findContours(img.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    area = []
    for c in contours:
        area.append(cv2.contourArea(c))
    cparea = area.copy()

    area.sort(reverse=True)
    ROI_tmp = np.zeros(img.shape, np.uint8)
    # for i in range(1, 10):
    #     # 选择最有可能的一个区域
    #     ROI_tmp = np.zeros(img.shape, np.uint8)
    #     max_idx = cparea.index(area[i])
    #
    #     # 强度匹配 因为直接映射到dcm上不用转uint8
    #     cv2.drawContours(ROI_tmp, contours, max_idx, (255, 255, 255), -1)
    #
    #     index = np.nonzero(ROI_tmp)
    #     mean = np.mean(img_o[index])
    #     std = np.std(img_o[index])
    #     # if mean > 90 or mean < 10 or std > 70 or std < 15:
    #     #     continue
    #
    #     s = pd.Series(img_o[index])
    #     piandu = s.skew()
    #     fengdu = s.kurt()
    #     # if piandu > 1 or fengdu < -5 or fengdu > 20:
    #     #     continue
    #
    #     # 生成矩
    #     M = cv2.moments(contours[max_idx])
    #
    #     # 面积周长
    #     perimeter = cv2.arcLength(contours[max_idx], True)
    #     # if area[i] > 2000 or area[i] < 500 or perimeter > 250 or perimeter < 80:
    #     #     continue
    #     if area[i] > 2000  or perimeter > 400 :
    #         continue
    #
    #     # if area[i] > 4000 or area[i] < 500 or perimeter > 400 :
    #     #     continue
    #     #
    #     # 椭圆拟合
    #     # try:
    #     #     (x, y), (MA, ma), angle = cv2.fitEllipse(contours[max_idx])
    #     #     if ma - MA > 25:
    #     #         continue
    #     #     # ellipse.append(ma-MA)
    #     # except:
    #     #     continue
    #
    #
    #     # img_o[]
    #
    #     # 加矩形框
    #     x, y, w, h = cv2.boundingRect(contours[max_idx])
    #     ROI = cv2.rectangle(ROI, (x, y), (x + w + 10, y + h + 10), (255, 255, 255), -1)
    #
    #     # 填充
    #     # cv2.drawContours(ROI, contours, max_idx, (255, 255, 255), -1)

    ROI_tmp[270:430, 200:300] = image[270:430, 200:300]

    cv2.imshow("Image", image)
    cv2.imshow("Image", ROI_tmp)
    cv2.waitKey(0)
    print(f"{train_data_path}ROI-{file_name}.png")
    # cv2.imwrite(f"{train_data_path}ROI-{file_name}.png", ROI, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])


def main():
    global w
    dcm_files, _ = get_train_files(train_data_path, file_type='dcm', all=False)
    for i in dcm_files:
        get_roi(i)


if __name__ == '__main__':
    main()
