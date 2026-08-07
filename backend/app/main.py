from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api.routers import auth, users, hardware, rentals
from app.exceptions.auth import AuthError
from app.exceptions.users import UserError
from app.exceptions.hardware import HardwareError
from app.exceptions.rentals import RentalError

app = FastAPI(title="Booksy Hardware Hub")

@app.exception_handler(AuthError)
async def auth_exception_handler(request: Request, exc: AuthError):
    if exc.headers:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail}, headers=exc.headers)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.exception_handler(UserError)
async def user_exception_handler(request: Request, exc: UserError):
    if exc.headers:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail}, headers=exc.headers)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.exception_handler(HardwareError)
async def hardware_exception_handler(request: Request, exc: HardwareError):
    if exc.headers:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail}, headers=exc.headers)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.exception_handler(RentalError)
async def rental_exception_handler(request: Request, exc: RentalError):
    if exc.headers:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail}, headers=exc.headers)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(hardware.router, prefix="/api/hardware", tags=["hardware"])
app.include_router(rentals.router, prefix="/api/rentals", tags=["rentals"])
