# AI Log

## Models and Schemas Creation
**Prompt used:**
> Create database models and Pydantic schemas for the following entities: User, Hardware, Rental, Audit. Database setup in app/db/base.py. Use Pydantic v2 syntax. Hardware status must be a Python Enum. All models must have proper relationships defined. Add \_\_init\_\_.py files. Update AI_LOG.md and README.md.

**What AI decided and why:**
- **Database Base:** Created `app/db/base.py` with SQLite setup since it's the required database for this project.
- **SQLAlchemy Models:** Created `User`, `Hardware`, and `Rental` in `app/models/` using `datetime.utcnow` for timestamps and proper relationships with `relationship()` and `ForeignKey`. Used standard `enum.Enum` for `HardwareStatus`. 
- **Pydantic Schemas:** Created schemas in `app/schemas/` with `ConfigDict(from_attributes=True)` per Pydantic v2 syntax. Used base classes (`UserBase`, `HardwareBase`, etc.) to reduce code duplication.
- **Directory Structure:** Put all code in `backend/app/` instead of root `app/`, as the python project environment (`pyproject.toml`, `uv.lock`) is scoped to `backend/`.

**Any correction I had to make:**
- **EmailStr validation**: The agent initially used plain `str` for the email field in UserSchema 
  to avoid a missing dependency. I identified this as a gap — without proper email validation, 
  the API would accept malformed emails like "notanemail". I added `email-validator` via 
  `uv add email-validator` and switched to Pydantic's `EmailStr` type, which enforces RFC 5322 
  email format at the schema level before data ever reaches the database.
- **datetime.now() as default**: Agent passed `datetime.now(timezone.utc)` directly as 
  a column default, which evaluates once at import time. All records would share the same 
  timestamp. Fixed by wrapping in a lambda or using SQLAlchemy's `func.now()`.
