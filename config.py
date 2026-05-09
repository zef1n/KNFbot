import os
from dotenv import load_dotenv

load_dotenv()

TOKEN_API = os.getenv("TOKEN_API")

if not TOKEN_API:
    raise ValueError("TOKEN_API не задан. Создайте файл .env на основе .env.example")
