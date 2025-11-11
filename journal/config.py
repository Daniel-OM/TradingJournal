
import os 

def load_env(path=".env"):
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue  # saltar líneas vacías o comentarios
            key, value = line.split("=", 1)
            os.environ[key] = value  # guarda la variable en el entorno

load_env()

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'journal', 'instance', 'media')
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}
MAX_IMAGE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_VIDEO_SIZE = 1 * 1024 * 1024 * 1024  # 1Gb
POLYGON_KEY = os.getenv("POLYGON_KEY", None)
POLYGON_FREE = os.getenv("POLYGON_FREE", "False").lower() in ("true", "1", "t")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", None)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
LOCAL_DB = f"sqlite:///path/trading_journal.db"
REMOTE_DB = os.getenv("REMOTE_DB")

class DevConfig:
    SECRET_KEY = 'tu_clave_secreta_aqui'
    TEMPLATES_AUTO_RELOAD = True
    SQLALCHEMY_DATABASE_URI = LOCAL_DB
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Verifica conexiones antes de usarlas
        "pool_recycle": 300,     # Tiempo en segundos antes de reciclar conexiones (para evitar desconexiones)
        "pool_size": 10,          # Número máximo de conexiones en el pool
        "max_overflow": 5,        # Número de conexiones extra si el pool está lleno
        "pool_timeout": 30,       # Tiempo máximo para esperar una conexión antes de error
    }
    APPLICATION_ROOT = '/'
    STATIC_URL_PATH = '/static'

class ProdConfig:
    SECRET_KEY = 'tu_clave_secreta_aqui'
    TEMPLATES_AUTO_RELOAD = True
    SQLALCHEMY_DATABASE_URI = REMOTE_DB
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Verifica conexiones antes de usarlas
        "pool_recycle": 300,     # Tiempo en segundos antes de reciclar conexiones (para evitar desconexiones)
        "pool_size": 10,          # Número máximo de conexiones en el pool
        "max_overflow": 5,        # Número de conexiones extra si el pool está lleno
        "pool_timeout": 30,       # Tiempo máximo para esperar una conexión antes de error
    }
    APPLICATION_ROOT = '/'
    STATIC_URL_PATH = '/static'