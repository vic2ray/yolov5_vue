from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from . import setting


db = SQLAlchemy()   # Create sqlalchemy application
from flask_socketio import SocketIO
socketio = SocketIO()


def create_app():
    app = Flask(__name__)
    app.config.from_object(setting.BaseConfig)      # 加载基础配置
    app.config.from_object(setting.SqliteConfig)    # 加载数据库配置
    CORS(app)

    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins='*')

    # try:
    #     os.makedirs(app.instance_path)
    # except OSError:
    #     pass

    from .views import dataset
    app.register_blueprint(dataset.ds)
    from .views import yolov
    app.register_blueprint(yolov.yv)
    from .views import annotate
    app.register_blueprint(annotate.anno)
    from .views import weight
    app.register_blueprint(weight.wt)

    return app

