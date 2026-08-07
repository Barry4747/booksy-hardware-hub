from fastapi import FastAPI
from app.api.routers import auth

app = FastAPI(title="Booksy Hardware Hub")

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
