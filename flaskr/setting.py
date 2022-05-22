# 基础配置
class BaseConfig(object):
    DEBUG = True
    PORT = 5000
    HOST = "0.0.0.0"


# sqlite3环境配置
class SqliteConfig(object):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///foo.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True


# mysql环境配置
class MysqlConfig(object):
    DB_HOST = "172.17.171.8"
    DB_PORT = 33066
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@' + DB_HOST + ':' + str(DB_PORT) + '/train_system?charset=utf8'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

