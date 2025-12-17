# app/main.py
from fastapi import FastAPI
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router

app = FastAPI(
    title="Secure Multi-Tenant Backend",
    version="0.1.0",
)

app.include_router(auth_router)
app.include_router(users_router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
