# app/main.py
from fastapi import FastAPI


def create_app():
    app = FastAPI()

    from app.api.v1.auth import router as auth_router
    from app.api.v1.users import router as users_router
    from app.routers.tenant_dashboard import router as tenant_router
    from app.routers.admin import router as admin_router

    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(tenant_router)
    app.include_router(admin_router)

    return app


app = create_app()
