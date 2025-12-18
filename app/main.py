# app/main.py
from fastapi import FastAPI

app = FastAPI(title="Secure Multi-Tenant Backend", version="0.1.0")

# include routers after app is created; import routers locally if needed
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.routers import admin, tenant_dashboard


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(admin.router)
app.include_router(tenant_dashboard.router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
