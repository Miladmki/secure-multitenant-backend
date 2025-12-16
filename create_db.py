from app.core.database import engine, Base
from app.models import user, refresh_token

Base.metadata.create_all(bind=engine)

print("Database tables created")
