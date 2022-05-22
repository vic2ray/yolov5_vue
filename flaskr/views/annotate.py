import os, json
from flask import (
    Blueprint, request, render_template, url_for, jsonify, current_app
)


anno = Blueprint('annotate', __name__, url_prefix='/annotate')
dataset_folder = "dataset/images"   # static/dataset
label_folder = "label"      # static/label
yolov_label_folder = "dataset/labels"  # static/yolov_label
default_dataset = "coco"     # static/dataset/example
default_label = "coco"   # static/label/example


@anno.route('/', methods=['GET'])
def index():
    dataset = request.args.get('dataset', default_dataset)
    # Read image files under: static/dataset/example
    dataset_path = os.path.join(current_app.static_folder, dataset_folder, dataset)
    read_image_files = list()
    for parent, dirnames, filenames in os.walk(dataset_path):
        for filename in filenames:
            # 格式为：url_for('static', 'dataset/example/dog.jpeg') 使Jinja2能够渲染
            img_file = url_for('static', filename=dataset_folder + '/' + dataset + '/' + filename)
            read_image_files.append(img_file)
    return render_template('index.html', readImageFiles=read_image_files)


@anno.route('/saveJson', methods=['POST'])
def save_json():
    # label_path: static/label/example
    saveJson = request.get_json()  # get label json from LabelImage
    label = saveJson.get('label', default_label)
    filename = saveJson['filename']
    data = saveJson['data']

    # static/label/example/filename.json
    label_path = os.path.join(current_app.static_folder, label_folder, label, filename)
    try:
        os.mkdir(os.path.join(current_app.static_folder, label_folder, label))
    except OSError:
        pass
    label_data = json.dumps(data, indent=4, ensure_ascii=False)  # Add indent
    with open(label_path, 'w', encoding='utf-8') as f:
        f.write(label_data)  # Save label data

    #  convert to yolov label
    filename = filename.split('.json')[0] + '.txt'
    yolov_label_path = os.path.join(current_app.static_folder, yolov_label_folder, label, filename)
    try:    # 创建 yolov_lable/coco 数据集文件夹
        os.mkdir(os.path.join(current_app.static_folder, yolov_label_folder, label))
    except OSError:
        pass
    label_data = str()
    for rect in data:
        mask = rect['rectMask']
        x_center = (mask['xMin'] + mask['width'] / 2) / mask['iWidth']
        y_center = (mask['yMin'] + mask['height'] / 2) / mask['iHeight']
        width = mask['width'] / mask['iWidth']
        height = mask['height'] / mask['iHeight']
        label_data = label_data + str(rect['labels']['labelName']) + ' ' + str(x_center) + ' ' + \
                     str(y_center) + ' ' + str(width) + ' ' + str(height) + '\n'

    with open(yolov_label_path, 'w', encoding='utf-8') as f:
        f.write(label_data)  # Save label data
        
    return jsonify(status="success")


@anno.route('/getJson', methods=['GET'])
def get_json():
    label = request.args.get('label', default_label)  # label name
    # label_path: static/label/example/filename.json
    filename = request.args.get('filename').split('.')[0] + ".json"
    label_path = os.path.join(current_app.static_folder, label_folder, label, filename)
    try:
        with open(label_path, 'r', encoding='utf-8') as f:
            label_json = f.read()  # Read saved label data
            label_json = json.loads(label_json)
        return jsonify(status="success", labelJson=label_json)
    except FileNotFoundError:
        return jsonify(status="fail")


@anno.route('/getDatasetList')
def change_dataset():
    # static/dataset
    dataset_dir = os.path.join(current_app.static_folder, dataset_folder)
    # ['coco', 'example']
    dataset_list = os.listdir(dataset_dir)
    resp = list()
    for dataset in dataset_list:
        data = dict()
        data['name'] = dataset
        for parent, dirnames, filenames in os.walk(os.path.join(dataset_dir, dataset)):
            for filename in filenames[:1]:
                # Get first image: /static/dataset/example/alley.jpg
                thumb_url = url_for('static', filename=dataset_folder + '/' + dataset + '/' + filename)
                data['thumb_url'] = request.url_root.rstrip('/') + thumb_url  # TODO 存在bug
        resp.append(data)

    return jsonify(resp)