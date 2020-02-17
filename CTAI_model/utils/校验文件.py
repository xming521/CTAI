import os


def get_train_files(data_path, file_type='dcm', all=True):
    file_type = '.' + file_type
    image_list, mask_list, ROI_list = [], [], []
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
        if file_type in i:
            image_list.append(i)
        if '_mask' in i:
            mask_list.append(i)

    # 校验文件正确

    return image_list, mask_list


if __name__ == '__main__':
    a, _ = get_train_files('../data/all/d2/')
    _, b = get_train_files('../data/out/')

    for i in range(len(a)):
        aa = a[i].split('/')[-1].replace('.dcm', '')
        bb = b[i].split('/')[-1].replace('_mask.png', '')
        if aa != bb:
            print(aa, bb, b[i])
            print(a[i] + 'file list error!')
    for i in range(len(b)):
        aa = a[i].split('/')[-1].replace('.dcm', '')
        bb = b[i].split('/')[-1].replace('_mask.png', '')
        if aa != bb:
            print(a[i] + 'file list error!')
