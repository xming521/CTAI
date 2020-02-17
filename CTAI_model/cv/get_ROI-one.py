import SimpleITK as sitk
import cv2
import numpy as np

image = sitk.ReadImage('../data/train/train/10087.dcm')
image = sitk.GetArrayFromImage(image)[0, :, :]

image[image < -300] = 0
image[image > 300] = 0

ROI = np.zeros(image.shape, np.uint8)
# 获取图像中的像素数据
slices = [image]

# 复制Dicom图像中的像素数据
img = slices[int(len(slices) / 2)].copy()
img = np.uint8(img)

kernel = np.ones((4, 4), np.uint8)
img = cv2.dilate(img, kernel, iterations=1)

# 对图像进行阈值分割
ret, img = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY_INV)

xxx = img
# 提取分割结果中的轮廓，并填充孔洞
im2, contours, x = cv2.findContours(img.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
# 需要反色处理一下  现在找的是白色的  应该是黑色的

# mask = np.zeros(img.shape, np.uint8)
# for contour in contours:
#     cv2.fillPoly(mask, [contour], 255)
# img[(mask > 0)] = 255


area = []
for c in contours:
    area.append(cv2.contourArea(c))
cparea = area.copy()

area.sort(reverse=True)

for i in range(3, 8):
    max_idx = cparea.index(area[i])
    perimeter = cv2.arcLength(contours[max_idx], True)
    if area[i] > 5000 or perimeter > 500:
        continue
    print('周长', perimeter)

    cv2.drawContours(ROI, contours, max_idx, (220, 20, 60), -1)

# max_idx = cparea.index(area[3])
# cv2.drawContours(ROI, contours, max_idx, (220, 20, 60), -1)
# cv2.drawContours(ROI, contours, max_idx, (220, 20, 60), -1)


# 对分割结果进行形态学的开操作
# kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
# img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

# plt.figure(figsize=(10, 7))
# plt.imshow(img, 'gray')
# plt.title('Mask')
# plt.show()


cv2.imshow("Image", ROI)
cv2.waitKey(0)
