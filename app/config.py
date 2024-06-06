from os import getenv
from dotenv import load_dotenv


load_dotenv()


DB_CONFIG: dict = {
    "host": getenv("POSTGRES_HOST", "localhost"),
    "port": getenv("POSTGRES_PORT", 5432),
    "user": getenv("POSTGRES_USER", "user"),
    "pass": getenv("POSTGRES_PASSWORD", ""),
    "name": getenv("POSTGRES_DB", "app_db"),
}
