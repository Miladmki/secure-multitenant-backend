import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME = os.getenv("PROJECT_NAME", "Secure Multi-Tenant Backend")

settings = Settings()
