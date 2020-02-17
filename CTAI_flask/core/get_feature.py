import inspect

import SimpleITK as sitk
import cv2
import numpy as np
import pandas as pd
from numba import jit

np.set_printoptions(suppress=True)  # 输出时禁止科学表示法，直接输出小数值

column_all_c = ['面积', '周长', '重心x', '重心y', '似圆度', '灰度均值', '灰度方差', '灰度偏度',
                '灰度峰态', '小梯度优势', '大梯度优势', '灰度分布不均匀性', '梯度分布不均匀性', '能量', '灰度平均', '梯度平均',
                '灰度均方差', '梯度均方差', '相关', '灰度熵', '梯度熵', '混合熵', '惯性', '逆差矩']

features_list = ['area', 'perimeter', 'focus_x', 'focus_y', 'ellipse', 'mean', 'std', 'piandu', 'fengdu',
                 'small_grads_dominance',
                 'big_grads_dominance', 'gray_asymmetry', 'grads_asymmetry', 'energy', 'gray_mean', 'grads_mean',
                 'gray_variance', 'grads_variance', 'corelation', 'gray_entropy', 'grads_entropy', 'entropy', 'inertia',
                 'differ_moment']


# 最后俩偏度 峰度


# 获取变量的名
def get_variable_name(variable):
    callers_local_vars = inspect.currentframe().f_back.f_locals.items()
    return [var_name for var_name, var_val in callers_local_vars if var_val is variable]


def glcm(img_gray, ngrad=16, ngray=16):
    '''Gray Level-Gradient Co-occurrence Matrix,取归一化后的灰度值、梯度值分别为16、16'''
    # 利用sobel算子分别计算x-y方向上的梯度值
    gsx = cv2.Sobel(img_gray, cv2.CV_64F, 1, 0, ksize=3)
    gsy = cv2.Sobel(img_gray, cv2.CV_64F, 0, 1, ksize=3)
    height, width = img_gray.shape
    grad = (gsx ** 2 + gsy ** 2) ** 0.5  # 计算梯度值
    grad = np.asarray(1.0 * grad * (ngrad - 1) / grad.max(), dtype=np.int16)
    gray = np.asarray(1.0 * img_gray * (ngray - 1) / img_gray.max(), dtype=np.int16)  # 0-255变换为0-15
    gray_grad = np.zeros([ngray, ngrad])  # 灰度梯度共生矩阵
    for i in range(height):
        for j in range(width):
            gray_value = gray[i][j]
            grad_value = grad[i][j]
            gray_grad[gray_value][grad_value] += 1
    gray_grad = 1.0 * gray_grad / (height * width)  # 归一化灰度梯度矩阵，减少计算量
    get_glcm_features(gray_grad)


@jit
def get_gray_feature():
    # 灰度特征提取算法
    hist = cv2.calcHist([image_ROI_uint8[index]], [0], None, [256], [0, 256])
    # 假的 还没用灰度直方图

    c_features['mean'].append(np.mean(image_ROI[index]))
    c_features['std'].append(np.std(image_ROI[index]))

    s = pd.Series(image_ROI[index])
    c_features['piandu'].append(s.skew())
    c_features['fengdu'].append(s.kurt())


def get_glcm_features(mat):
    '''根据灰度梯度共生矩阵计算纹理特征量，包括小梯度优势，大梯度优势，灰度分布不均匀性，梯度分布不均匀性，能量，灰度平均，梯度平均，
    灰度方差，梯度方差，相关，灰度熵，梯度熵，混合熵，惯性，逆差矩'''
    sum_mat = mat.sum()
    small_grads_dominance = big_grads_dominance = gray_asymmetry = grads_asymmetry = energy = gray_mean = grads_mean = 0
    gray_variance = grads_variance = corelation = gray_entropy = grads_entropy = entropy = inertia = differ_moment = 0
    for i in range(mat.shape[0]):
        gray_variance_temp = 0
        for j in range(mat.shape[1]):
            small_grads_dominance += mat[i][j] / ((j + 1) ** 2)
            big_grads_dominance += mat[i][j] * j ** 2
            energy += mat[i][j] ** 2
            if mat[i].sum() != 0:
                gray_entropy -= mat[i][j] * np.log(mat[i].sum())
            if mat[:, j].sum() != 0:
                grads_entropy -= mat[i][j] * np.log(mat[:, j].sum())
            if mat[i][j] != 0:
                entropy -= mat[i][j] * np.log(mat[i][j])
                inertia += (i - j) ** 2 * np.log(mat[i][j])
            differ_moment += mat[i][j] / (1 + (i - j) ** 2)
            gray_variance_temp += mat[i][j] ** 0.5

        gray_asymmetry += mat[i].sum() ** 2
        gray_mean += i * mat[i].sum() ** 2
        gray_variance += (i - gray_mean) ** 2 * gray_variance_temp
    for j in range(mat.shape[1]):
        grads_variance_temp = 0
        for i in range(mat.shape[0]):
            grads_variance_temp += mat[i][j] ** 0.5
        grads_asymmetry += mat[:, j].sum() ** 2
        grads_mean += j * mat[:, j].sum() ** 2
        grads_variance += (j - grads_mean) ** 2 * grads_variance_temp
    small_grads_dominance /= sum_mat
    big_grads_dominance /= sum_mat
    gray_asymmetry /= sum_mat
    grads_asymmetry /= sum_mat
    gray_variance = gray_variance ** 0.5
    grads_variance = grads_variance ** 0.5
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            corelation += (i - gray_mean) * (j - grads_mean) * mat[i][j]
    glgcm_features = [small_grads_dominance, big_grads_dominance, gray_asymmetry, grads_asymmetry, energy, gray_mean,
                      grads_mean,
                      gray_variance, grads_variance, corelation, gray_entropy, grads_entropy, entropy, inertia,
                      differ_moment]
    for i in range(len(glgcm_features)):
        t = get_variable_name(glgcm_features[i])[0]
        c_features[t].append(np.round(glgcm_features[i], 4))


def get_geometry_feature():
    # 形态特征  分割mask获得一些特征
    im2, contours, x = cv2.findContours(mask_array.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    tarea = []
    tperimeter = []
    for c in contours:
        # 生成矩
        try:
            M = cv2.moments(c)
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            c_features['focus_x'].append(cx)
            c_features['focus_y'].append(cy)
        except:
            print('error')

        # 椭圆拟合
        try:
            (x, y), (MA, ma), angle = cv2.fitEllipse(c)
            c_features['ellipse'].append((ma - MA))
        except:
            continue
        # 面积周长
        tarea.append(cv2.contourArea(c))
        tperimeter.append(cv2.arcLength(c, True))

    # 将mask里的最大值追加 有黑洞
    try:
        c_features['area'].append(max(tarea))
        c_features['perimeter'].append(round(max(tperimeter), 4))
    except:
        print('area error')


# 提取肿瘤特征
def get_feature(image, mask):
    global w
    global image_ROI_uint8, index, image_ROI_mini, image_ROI, mask_array

    mask_array = cv2.imread(mask, 0)
    image = sitk.ReadImage(image)
    image_arrary = sitk.GetArrayFromImage(image)[0, :, :]
    # 映射到CT获得特征
    image_ROI = np.zeros(shape=image_arrary.shape)
    index = np.nonzero(mask_array)
    if not index[0].any():
        # c_features['no'] = True
        return None
    image_ROI[index] = image_arrary[index]
    image_ROI_uint8 = np.uint8(image_ROI)
    # 获得只有肿瘤的图片
    x, y, w, h = cv2.boundingRect(mask_array)
    image_ROI_mini = np.uint8(image_arrary[y:y + h, x:x + w])
    w = image_ROI_mini

    # 灰度梯度共生矩阵提取纹理特征

    get_geometry_feature()

    get_gray_feature()

    glcm(image_ROI_mini, 15, 15)

    return c_features


def main(pid):
    global w

    person_id = pid
    global c_features
    c_features = {}
    for i in range(len(features_list)):
        c_features[features_list[i]] = [column_all_c[i]]

    get_feature(f'tmp/ct/{pid}.dcm', f'tmp/mask/{pid}_mask.png')

    for j in c_features:
        if j == 'id':
            continue
        c_features[j][1] = np.round(np.mean(c_features[j][1]), 4)

    return c_features


if __name__ == '__main__':
    main()
