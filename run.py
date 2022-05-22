import subprocess
from flaskr import create_app, db, setting


if __name__ == '__main__':
    log_pipe = subprocess.Popen('tensorboard --logdir train --host 0.0.0.0', shell=True)
    app = create_app()
    db.create_all(app=app)  # Create tables
    app.run(port=setting.BaseConfig.PORT,
            host=setting.BaseConfig.HOST)