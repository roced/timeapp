import os
import logging
from logging.handlers import RotatingFileHandler

# This points to the root directory (where app.db is)
basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    # This will look for app.db in the root directory
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Logging configuration
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    LOG_FILE = os.path.join(basedir, 'logs/timeapp.log')  # Also updated to use basedir
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 10

    # Admin user configuration
    ADMIN_USERNAME = 'admin'
    ADMIN_EMAIL = 'admin@example.com'
    ADMIN_PASSWORD = 'admin123'  # Change this in production!

    @staticmethod
    def init_app(app):
        # Create logs directory in root folder
        logs_dir = os.path.join(basedir, 'logs')
        if not os.path.exists(logs_dir):
            os.mkdir(logs_dir)

        if Config.LOG_TO_STDOUT:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(logging.Formatter(Config.LOG_FORMAT))
            stream_handler.setLevel(Config.LOG_LEVEL)
            app.logger.addHandler(stream_handler)
        else:
            file_handler = RotatingFileHandler(
                Config.LOG_FILE,
                maxBytes=Config.LOG_MAX_SIZE,
                backupCount=Config.LOG_BACKUP_COUNT
            )
            file_handler.setFormatter(logging.Formatter(Config.LOG_FORMAT))
            file_handler.setLevel(Config.LOG_LEVEL)
            app.logger.addHandler(file_handler)

        app.logger.setLevel(Config.LOG_LEVEL)
        app.logger.info('TimeApp startup')

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    pass

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}