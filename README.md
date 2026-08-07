# booksy-hardware-hub

## Fully Implemented
- Database setup (`app/db/base.py`)
- SQLAlchemy Models (`app/models/user.py`, `app/models/hardware.py`, `app/models/rental.py`)
- Pydantic v2 Schemas (`app/schemas/user.py`, `app/schemas/hardware.py`, `app/schemas/rental.py`, `app/schemas/audit.py`)
- Seed script with anomaly detection (`app/db/seed.py`)
- Admin user creation script (`create_admin.py`)
- Password hashing and JWT token management (`app/core/security.py`)
- Repository layer (`app/repositories/users.py`)
- Service layer (`app/services/auth.py`)
- Dependency injection (`app/api/dependencies/core.py`)
- API Auth Routers (`app/api/routers/auth.py`, `app/main.py`)

## Shortcuts