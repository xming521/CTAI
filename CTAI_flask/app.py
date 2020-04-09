import datetime
import logging as rel_log
import os
import shutil
from datetime import timedelta

import torch
from flask import *

import core.main
import core.net.unet as net

UPLOAD_FOLDER = r'./uploads'

ALLOWED_EXTENSIONS = set(['dcm'])
app = Flask(__name__)
app.secret_key = 'secret!'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

werkzeug_logger = rel_log.getLogger('werkzeug')
werkzeug_logger.setLevel(rel_log.ERROR)

# 解决缓存刷新问题
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)


# 添加header解决跨域
@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'
    return response


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/')
def hello_world():
    return redirect(url_for('static', filename='./index.html'))


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    file = request.files['file']
    print(datetime.datetime.now(), file.filename)
    if file and allowed_file(file.filename):
        src_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(src_path)
        shutil.copy(src_path, './tmp/ct')
        image_path = os.path.join('./tmp/ct', file.filename)
        # print(image_path)
        pid, image_info = core.main.c_main(image_path, current_app.model)
        return jsonify({'status': 1,
                        'image_url': 'http://127.0.0.1:5003/tmp/image/' + pid,
                        'draw_url': 'http://127.0.0.1:5003/tmp/draw/' + pid,
                      'image_info': image_info
                       })


    return jsonify({'status': 0})


@app.route("/download", methods=['GET'])
def download_file():
    # 需要知道2个参数, 第1个参数是本地目录的path, 第2个参数是文件名(带扩展名)
    return send_from_directory('data', 'testfile.zip', as_attachment=True)


# show photo
@app.route('/tmp/<path:file>', methods=['GET'])
def show_photo(file):
    # print(file)
    if request.method == 'GET':
        if file is None:
            pass
        else:
            image_data = open(f'tmp/{file}', "rb").read()
            response = make_response(image_data)
            response.headers['Content-Type'] = 'image/png'
            return response
    else:
        pass


def init_model():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = net.Unet(1, 1).to(device)
    if torch.cuda.is_available():
        model.load_state_dict(torch.load("./core/net/model.pth"))
    else:
        model.load_state_dict(torch.load("./core/net/model.pth", map_location='cpu'))
    model.eval()
    return model


if __name__ == '__main__':
    with app.app_context():
        current_app.model = init_model()
    app.run(host='127.0.0.1', port=5003, debug=True)
