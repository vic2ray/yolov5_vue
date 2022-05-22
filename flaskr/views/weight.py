import os, time
from flask import Blueprint, request, jsonify, current_app


wt = Blueprint('weight', __name__, url_prefix='/weight')
pre_weight_path = os.path.join(os.getcwd(), 'weights')
user_weight_path = os.path.join(os.getcwd(), 'train')


def timestamp_to_time(timestamp):
    time_struct = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', time_struct)


@wt.route('/retrieve')      # 查询权重信息
def retrieve():
    resp = list()

    # 查找预训练权重
    for weight_name in os.listdir(pre_weight_path):
        weight = dict()
        weight['name'] = weight_name
        weight['data_size'] = str(os.path.getsize(os.path.join(pre_weight_path, weight_name)) // 1024 //1024) + " MB"
        weight['create_time'] = timestamp_to_time(os.path.getctime(os.path.join(pre_weight_path, weight_name)))
        weight['update_time'] = timestamp_to_time(os.path.getmtime(os.path.join(pre_weight_path, weight_name)))
        resp.append(weight)

    # 查找用户自定义训练权重
    weights_folder = os.listdir(user_weight_path)    # train/coco
    for dataset in weights_folder:
        # train/coco/weights/best.pt
        user_weight_path_folder = os.path.join(user_weight_path, dataset, 'weights')
        dataset_weights = os.listdir(user_weight_path_folder)
        for dataset_weight in dataset_weights:
            weight = dict()
            weight['name'] = dataset + '-' + dataset_weight
            weight['data_size'] = str(os.path.getsize(os.path.join(user_weight_path_folder, dataset_weight)) // 1024 // 1024) + " MB"
            weight['create_time'] = timestamp_to_time(os.path.getctime(os.path.join(user_weight_path_folder, dataset_weight)))
            weight['update_time'] = timestamp_to_time(os.path.getmtime(os.path.join(user_weight_path_folder, dataset_weight)))
            resp.append(weight)

    return jsonify(resp)


@wt.route('/delete')
def delete():
    resp = dict()
    weight = request.args.get('name')
    # if weight not in ['yolov5s.pt', 'yolov5m.pt', 'yolov5l.pt', 'yolov5x.pt']:
    if '-' in weight:   # dataset-best.pt or dataset-last.pt
        dataset, weight = weight.split('-')
        user_weight_path_folder = os.path.join(user_weight_path, dataset, 'weights', weight)
        try:
            os.remove(user_weight_path_folder)
            resp['status'] = 'success'
        except OSError as e:
            resp['status'] = 'fail'
            resp['error'] = str(e)
    elif weight not in ['yolov5s.pt', 'yolov5m.pt', 'yolov5l.pt', 'yolov5x.pt']:
        try:
            os.remove(os.path.join(pre_weight_path, weight))
            resp['status'] = 'success'
        except OSError as e:
            resp['status'] = 'fail'
            resp['error'] = str(e)
    else:
        resp['status'] = 'fail'
        resp['error'] = '预置权重不可删除！'

    return jsonify(resp)


@wt.route('/create', methods=['POST'])
def create():
    file = request.files.get('file')
    # print(dir(file))
    resp = dict()
    try:
        # with open(os.path.join(pre_weight_path, file.filename), 'wb') as f:
        #     f.write(file)
        #     pass
        file.save(os.path.join(pre_weight_path, file.filename))
        resp['status'] = 'success'
    except Exception as e:
        resp['status'] = 'fail'
        resp['error'] = str(e)

    return jsonify(resp)
