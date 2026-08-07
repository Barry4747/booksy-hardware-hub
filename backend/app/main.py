from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api.routers import auth
from app.exceptions.auth import AuthError

app = FastAPI(title="Booksy Hardware Hub")

@app.exception_handler(AuthError)
async def auth_exception_handler(request: Request, exc: AuthError):
    if exc.headers:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail}, headers=exc.headers)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
