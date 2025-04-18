# config.py
import os

class Config:
    DB_HOST = "127.0.0.1"
    DB_SOCKET = None
    DB_NAME = "inventario"
    DB_USER = "root"
    DB_PASS = "hjb38u30"
    DB_PORT = "3306"


    # Generate a secret key if it doesn't exist
    SECRET_KEY = os.environ.get("SECRET_KEY", "my_secret_key")
    if not SECRET_KEY:
        import secrets
        SECRET_KEY = secrets.token_hex(16)
