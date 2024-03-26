from os import getenv
from dotenv import load_dotenv

load_dotenv()

DB_HOST = getenv("DB_HOST")
DB_PORT = getenv("DB_PORT")
DB_NAME = getenv("DB_NAME")
DB_USER = getenv("DB_USER")
DB_PASS = getenv("DB_PASS")

DATABASE_URL = f"postgres://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

DATABASE_CONFIG = {
    "connections": {
        "default": DATABASE_URL,
    },
    "apps": {
        "models": {
            "models": [
                "aerich.models",
                "users.models",
                "sales.models",
            ],
            "default_connection": "default",
        },
    },
}

JWT_SECRET_KEY = getenv("JWT_SECRET_KEY")
VERIFY_SECRET_KEY = getenv("VERIFY_SECRET_KEY")
ALGORITHM = getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 465
EMAIL_HOST_USER = getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = getenv('EMAIL_HOST_PASSWORD')


#DB_HOST_TEST = os.environ.get("DB_HOST_TEST")
#DB_PORT_TEST = os.environ.get("DB_PORT_TEST")
#DB_NAME_TEST = os.environ.get("DB_NAME_TEST")
#DB_USER_TEST = os.environ.get("DB_USER_TEST")
#DB_PASS_TEST = os.environ.get("DB_PASS_TEST")