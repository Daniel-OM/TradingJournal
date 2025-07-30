
import os 

UPLOAD_FOLDER = 'instance/media'
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}
MAX_IMAGE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_VIDEO_SIZE = 1 * 1024 * 1024 * 1024  # 1Gb

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class DevConfig:
    SECRET_KEY = 'tu_clave_secreta_aqui'
    SQLALCHEMY_DATABASE_URI = f"sqlite:///path/trading_journal.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APPLICATION_ROOT = '/'  # desarrollo
    STATIC_URL_PATH = '/static'

class ProdConfig:
    SECRET_KEY = 'tu_clave_secreta_aqui'
    SQLALCHEMY_DATABASE_URI = f"sqlite:///path/trading_journal.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APPLICATION_ROOT = '/trading-journal'
    STATIC_URL_PATH = '/trading-journal/static'