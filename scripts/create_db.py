import sys, os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from app.core.database import engine, Base
from app.models import user, refresh_token, tenant, role

Base.metadata.create_all(bind=engine)
print("Database tables created in data/secure_backend.db")
