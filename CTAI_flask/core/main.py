from core import process, predict, get_feature


def c_main(path,model):
    image_data = process.pre_process(path)
    # print(image_data)
    predict.predict(image_data,model)
    process.last_process(image_data[1])
    image_info = get_feature.main(image_data[1])

    return image_data[1] + '.png', image_info


if __name__ == '__main__':
    pass
