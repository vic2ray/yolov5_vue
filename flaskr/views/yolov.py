# *
# * Upload a image file
# * Auth: june
# * 2020年11月12日17:37:37
# *

import os, subprocess, base64, yaml, shutil, time
from flask import Blueprint, request, current_app, jsonify
from flaskr import socketio

yv = Blueprint('yolov', __name__, url_prefix='/yolov')
yolov_label_folder = "dataset/labels"


@yv.route('/detect', methods=['POST'])
def upload():
    # 获取权重参数
    weight = request.args.get('weight', 'yolov5s.pt')
    # 接收前端上传图片
    upload_img = request.files['file']
    print("Received image", upload_img.filename)

    # 清理 inference/images 图片
    for p, d, f in os.walk('detect/image'):
      for fname in f:
          os.remove(os.path.join(p, fname))
    # 清理 inference/output 图片
    # for p, d, f in os.walk('inference/output'):
    #   for fname in f:
    #       os.remove(os.path.join(p, fname))
    # 新版本yolov5，删除 output 文件夹
    try:
        shutil.rmtree('detect/output')
    except FileNotFoundError:
        pass

    # 保存图片到 inference/images
    upload_img.save(os.path.join('detect/image', upload_img.filename))

    # 检测 weight 路径
    # if weight not in ['yolov5s.pt', 'yolov5m.pt', 'yolov5l.pt', 'yolov5x.pt']:
    if '-' in weight:
        weight = os.path.join('train', weight.split('-')[0], 'weights', weight.split('-')[1])
    else:
        weight = os.path.join('weights', weight)

    # 执行python detect.py
    yolov5_detect_path = os.path.join(current_app.root_path, 'yolov5', 'detect.py')
    cmd_cpu = 'python %s --weights %s --source detect/image/%s --project detect --name output' % \
          (yolov5_detect_path, weight, upload_img.filename)
    pipeline = subprocess.Popen(cmd_cpu, stdout=subprocess.PIPE, shell=True)
    while True:
        for line in iter(pipeline.stdout.readline, b''):
            print(line.decode('gbk').strip())
        if pipeline.poll() is not None:
            pipeline.kill()
            break

    # 读取 yolov 侦测结果
    detected_img_stream = None    # 返回 base64 图片编码
    with open(os.path.join('detect/output', upload_img.filename), 'rb') as f:
        detected_img = f.read()
        detected_img_stream = base64.b64encode(detected_img).decode()

    return detected_img_stream


@yv.route('/get_weights')
def get_weights():
    # 查找预训练权重
    yolov5_weights_path = os.path.join(os.getcwd(), 'weights')
    weights = os.listdir(yolov5_weights_path)
    # 查找用户自定义训练权重
    custom_weights_path = os.path.join(os.getcwd(), 'train')    # train
    weights_folder = os.listdir(custom_weights_path)    # train/coco
    for dataset in weights_folder:
        # train/coco/weights/best.pt
        dataset_weights = os.listdir(os.path.join(custom_weights_path, dataset, 'weights'))
        for dataset_weight in dataset_weights:
            weights.append(dataset + '-' + dataset_weight)
    return jsonify(weights)


@yv.route('/check_labels')
def check_labels():
    dataset = request.args.get('dataset')
    dataset_path = os.path.join(current_app.static_folder, 'dataset/images', dataset)
    yolov_label_path = os.path.join(current_app.static_folder, 'dataset/labels', dataset)

    resp = dict()
    resp['dataset_length'] = len(os.listdir(dataset_path))
    try:
        resp['label_length'] = len(os.listdir(yolov_label_path))
    except FileNotFoundError:
        resp['label_length'] = 0

    return jsonify(resp)


# 检查所选数据集是否存在已训练权重
@yv.route('/preTrain')
def pre_train():
    dataset = request.args.get('dataset')
    resp = dict()
    if os.path.exists(os.path.join('train', dataset, 'weights', 'best.pt')):
        resp['exists'] = True
    else:
        resp['exists'] = False
    return resp


@yv.route('/train', methods=['POST'])
def train():
    dataset = request.form.get('dataset', 'coco')   # 获取待训练数据集
    weight = request.form.get('weight', 'yolov5s.pt')   # 获取预训练权重
    model = request.form.get('model', 'yolov5s.yaml')  # 选择 model 文件
    epochs = request.form.get('epochs', 300)
    batch = request.form.get('batch', 16)
    other = request.form.get('other', '')
    # print(request.form)
    resp = dict()

    # 从标签内容写 data/coco.yaml 文件
    yolov_label_path = os.path.join(current_app.static_folder, yolov_label_folder, dataset)
    if not os.path.exists('data/%s.yaml' % dataset):
        with open('data/%s.yaml' % dataset, 'w'):
            pass    # 不存在则创建空文件！
    with open('data/%s.yaml' % dataset, 'r+', encoding='utf-8') as f:
        yaml_data = yaml.safe_load(f)       # 读取 yaml 属性
        if yaml_data is None:
            yaml_data = {
                'train': 'flaskr/static/dataset/images/' + dataset,    # 数据集路径
                'val': 'flaskr/static/dataset/images/' + dataset,
                'nc': 0,    # 类数量
                'names': [],    # 类列表
            }
            yaml.dump(yaml_data, f)
        # 遍历标签，增加标签名和数量，替换类名为数字索引
        for label_name in os.listdir(yolov_label_path):
            rewrite_flag = False
            with open(os.path.join(yolov_label_path, label_name), encoding='utf-8') as f1, \
                    open("%s.bak" % os.path.join(yolov_label_path, label_name), "a", encoding="utf-8") as f2:
                for line in f1.readlines():
                    name = line.strip().split()[0]
                    if not name.isnumeric() and name not in yaml_data['names']:      # 不存在类名，新增
                        f.seek(0)  # 跳到文本首字节
                        f.truncate()  # 清空文本内容
                        yaml_data['names'].append(name)
                        yaml_data['nc'] = yaml_data['nc'] + 1
                        yaml.dump(yaml_data, f)

                    if not name.isnumeric():    # 存在类名，重写文件
                        rewrite_flag = True
                        line = line.replace(name, str(yaml_data['names'].index(name)))
                        f2.write(line)

            if rewrite_flag:
                os.remove(os.path.join(yolov_label_path, label_name))
                os.rename("%s.bak" % os.path.join(yolov_label_path, label_name), os.path.join(yolov_label_path, label_name))
            else:
                os.remove("%s.bak" % os.path.join(yolov_label_path, label_name))

    # 修改 models/yolov5s.yaml 内的 nc 类数量
    # with open('models/%s.yaml' % cfg, 'r+', encoding='utf-8') as f:
    #     yolov_yaml_data = yaml.safe_load(f)
    #     if yolov_yaml_data['nc'] != yaml_data['nc']:
    #         yolov_yaml_data['nc'] = yaml_data['nc']
    #
    #         f.seek(0)  # 跳到文本首字节
    #         f.truncate()  # 清空文本内容
    #         yaml.safe_dump(yolov_yaml_data, f, default_flow_style=False)
    # 仅当不使用预训练权重，重头训练时需要更改！！！

    # train
    print("Start train...")
    yolov5_train_path = os.path.join(current_app.root_path, 'yolov5', 'train.py')
    cmd = 'python {train_path} --data data/{dataset}.yaml --cfg models/{model} --weights weights/{weight}' \
          ' --batch {batch} --epochs {epochs} {other_opts} --project train --name {name} --exist-ok'.\
        format(train_path=yolov5_train_path, dataset=dataset, model=model, weight=weight,
               batch=batch, epochs=epochs, other_opts=other, name=dataset)
    print(cmd)
    pipeline = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                shell=True)
    while True:
        for line in iter(pipeline.stdout.readline, b''):
            try:
                outputs = line.decode('gbk').strip()
            except Exception as e:
                outputs = line.decode('utf-8').strip()
            print(outputs)
            # socket.io 输出日志
            socketio.emit('response', {
                'data': outputs
            }, namespace='/test')
            socketio.sleep(0)
            # 粗暴终结训练进程
            if "epochs completed" in outputs:
                pipeline.kill()     # 结束子进程
                # os.killpg(pipeline.pid, 9)
                return resp
            # 启动日志显示面板
            # if "Start Tensorboard" in outputs:
            #     log_cmd = 'tensorboard --logdir train'
            #     log_pipe = subprocess.Popen(log_cmd)
        if pipeline.poll() is not None:
            break

    resp['status'] = 'success'
    return jsonify(resp)


from flask_socketio import emit
@socketio.on('connect', namespace='/test')
def test_connect():
    print('connected.....')


@socketio.on('fuck', namespace='/test')
def test_connect(data):
    print("emmit", data)
    # socketio.emit('response',
    #     {'data': 'connected and fuck you back! '}, namespace='/test')
    # print('emit ends')

    cmd = 'ping baidu.com'
    pipeline = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    while True:
        for line in iter(pipeline.stdout.readline, b''):
            outputs = line.decode('gbk').strip()
            print(outputs)
            socketio.emit('response', {
                'data': outputs
            }, namespace='/test')
            socketio.sleep(0)
        if pipeline.poll() is not None:
            break


@yv.route('/test')
def test():
    cmd = 'ping baidu.com'
    pipeline = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    while True:
        for line in iter(pipeline.stdout.readline, b''):
            outputs = line.decode('gbk').strip()
            print(outputs)
            socketio.emit('response', {
                'data': outputs
            }, namespace='/test')
            socketio.sleep(0)
        if pipeline.poll() is not None:
            break
    return 'xxx'