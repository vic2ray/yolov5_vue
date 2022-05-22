import os, shutil
from flask import Blueprint, request, jsonify, current_app, url_for

from flaskr import db
from flaskr.model import Dataset

ds = Blueprint('dataset', __name__, url_prefix='/dataset')
dataset_folder = "dataset/images"   # static/dataset/images
label_folder = "label"  # static/label
yolov_label_folder = "dataset/labels"  # static/dataset/labels


@ds.route('/create', methods=['POST'])
def create():
    req = request.get_json()
    name = req.get('name')
    desc = req.get('desc', None)
    resp = dict()

    try:    # create instance folder
        os.makedirs(os.path.join(current_app.static_folder, dataset_folder, name))
    except OSError:
        resp['status'] = 'fail'
        resp['error'] = "Dataset instance folder already exists. "
        return jsonify(resp)

    dataset = Dataset(name=name, desc=desc)
    try:
        db.session.add(dataset)
        db.session.commit()
        resp['status'] = 'success'
    except Exception as e:
        db.session.rollback()
        resp['status'] = 'fail'
        resp['error'] = str(e)

    return jsonify(resp)


@ds.route('/rechieve', methods=['GET'])
def retrieve():
    datasets = list()
    results = Dataset.query.all()
    for result in results:
        dataset = dict()
        dataset['name'] = result.name
        dataset['desc'] = result.desc
        dataset['data_row'] = result.data_row
        dataset['create_time'] = result.create_time.strftime('%Y-%m-%d %H:%M:%S')
        dataset['update_time'] = result.update_time.strftime('%Y-%m-%d %H:%M:%S')
        datasets.append(dataset)

    return jsonify(datasets)


@ds.route('/update', methods=['POST'])
def update():
    name = request.form.get('name')

    resp = dict()
    for file in request.files.getlist('file'):
        img_path = os.path.join(current_app.static_folder, dataset_folder, name, file.filename)
        if not os.path.exists(img_path):
            file.save(img_path)     # save image
            try:    # update data_row
                data = Dataset.query.filter_by(name=name).first()
                # print(data_row.data_row, type(data_row))
                Dataset.query.filter_by(name=name).update({'data_row': data.data_row+1})
                db.session.commit()
                resp['status'] = 'success'
            except Exception as e:
                resp['status'] = 'fail'
                resp['error'] = str(e)
        else:
            resp['status'] = 'fail'
            resp['error'] = 'image already exists. '

    return jsonify(resp)


@ds.route('/delete', methods=['GET'])
def delete():
    name = request.args.get('name')

    resp = dict()
    try:
        # 删除数据集目录
        try:
            shutil.rmtree(os.path.join(current_app.static_folder, dataset_folder, name))
        except:
            pass
        # 删除标注目录
        try:
            shutil.rmtree(os.path.join(current_app.static_folder, label_folder, name))
        except:
            pass
        try:
            shutil.rmtree(os.path.join(current_app.static_folder, yolov_label_folder, name))
        except:
            pass
        # 删除训练配置 data/coco.yaml
        try:
            os.remove(os.path.join(os.getcwd(), 'data', "{}.yaml".format(name)))
        except:
            pass
        # 删除数据库记录
        Dataset.query.filter_by(name=name).delete()
        db.session.commit()
        resp['status'] = 'success'
    except Exception as e:
        db.session.rollback()
        resp['status'] = 'fail'
        resp['error'] = str(e)

    return jsonify(resp)