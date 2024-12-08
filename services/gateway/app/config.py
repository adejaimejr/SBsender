import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")
    CLIENT_SERVICE_URL = os.getenv("CLIENT_SERVICE_URL", "http://localhost:8001")
    WEBHOOK_SERVICE_URL = os.getenv("WEBHOOK_SERVICE_URL", "http://localhost:8002")
    MESSAGE_SERVICE_URL = os.getenv("MESSAGE_SERVICE_URL", "http://localhost:8003")
    HISTORY_SERVICE_URL = os.getenv("HISTORY_SERVICE_URL", "http://localhost:8004")

settings = Settings()
