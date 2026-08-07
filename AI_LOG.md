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

## Seed and Admin Scripts Creation
**Prompt used:**
> Create two scripts in backend/: app/db/seed.py to load and process hardware seed data with anomaly detection, and create_admin.py to create an admin user using passlib bcrypt. Create an empty app/db/seed_data.json. Update AI_LOG.md and README.md.

**What AI decided and why:**
- **Seed script (app/db/seed.py):** Implemented logging to report anomalies as requested. Structured data cleaning around `HardwareStatus` parsing, date formatting (supports multiple formats), and handled notes/history transformations. Made it idempotent by checking if `Hardware.id` exists before inserting.
- **Admin script (create_admin.py):** Utilized `passlib.context.CryptContext` with bcrypt to hash passwords. Reads `ADMIN_EMAIL` and `ADMIN_PASSWORD` from environment with a fallback to interactive prompt using `getpass`.
- **Empty Seed JSON:** Created `backend/app/db/seed_data.json` containing just `[]`.

**Any correction I had to make:**
- **In-memory duplicate detection**: The initial implementation only queried the database 
  to detect duplicate IDs. This missed duplicates within the seed file itself — if two 
  records with the same ID appear in seed_data.json, the first would be added to the 
  session but not yet committed, so the second DB query would find nothing and both would 
  be inserted, causing a primary key violation on commit. Fixed by tracking seen IDs in 
  a set before any DB interaction.

- **difflib for typo detection**: Replaced the custom substring/length heuristic with 
  Python's built-in difflib.get_close_matches, which uses SequenceMatcher for more 
  accurate similarity scoring. cutoff=0.7 catches clear typos like "appel" while 
  avoiding false positives on unrelated brand names.

- **Session not closed on error**: The agent placed `db.close()` outside the try/except 
  block. If an exception occurred before reaching that line, the session would leak. 
  I wrapped the entire seeding logic in a try/except/finally block to guarantee the 
  session is always closed.

- **Unrecognized date format not handled**: The original `parse_date` function returned 
  `None, False` for completely unrecognized formats, silently discarding the anomaly. 
  I added a third case that returns `None, True` so the anomaly counter increments and 
  the issue is logged.

## Security Implementation
**Prompt used:**
> In backend/app/core/security.py implement Password hashing and verification using passlib bcrypt, JWT access token creation and decoding using python-jose, JWT refresh token creation and decoding. Read SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS from app/core/config.py (pydantic-settings). Use python-jose, not PyJWT. Update AI_LOG and README.

**What AI decided and why:**
- **Security Utilities (app/core/security.py):** Implemented all requested JWT operations (`create_access_token`, `create_refresh_token`, `decode_token`) using `python-jose` as specified. Also set up `CryptContext` from `passlib` to hash and verify passwords using bcrypt.
- **Config check:** Verified that `config.py` correctly uses `pydantic-settings` to load the variables from the `.env` file (which you already implemented beautifully!).
- **Admin Script Refactoring:** Updated `create_admin.py` to import `get_password_hash` directly from `security.py`, adhering to DRY principles.

**Any correction I had to make:**
- **`datetime.utcnow()` deprecation:** Replaced `datetime.utcnow()` with timezone-aware `datetime.now(timezone.utc)` when calculating token expiration. `utcnow()` is deprecated in Python 3.12+ and using timezone-aware objects is a more robust practice for JWT tokens.

## Service & Repository Architecture (Users & Auth)
**Prompt used:**
> In backend/app/repositories/users.py implement UserRepository. In backend/app/services/auth.py implement AuthService (login, logout, refresh, me) using HttpOnly cookies. Repositories must use db.add() and db.flush() only — never db.commit(). Commit belongs to the service layer as a single Unit of Work. Register UserRepository and AuthService in app/api/dependencies/core.py. Update AI_LOG and README.

**What AI decided and why:**
- **UserRepository (`app/repositories/users.py`):** Implemented strict repository pattern wrapping `Session`. As requested, strictly avoided `db.commit()` in favor of `db.flush()` so that the database transaction remains open for the service layer to control.
- **AuthService (`app/services/auth.py`):** Implemented token generation, cookie management (using `Secure`, `HttpOnly`, and `Lax`), and core auth logic cleanly separating it from API routing. The service receives `db` to orchestrate Unit of Work commits if needed in the future (e.g. for `last_login` updates).
- **Dependencies (`app/api/dependencies/core.py`):** Created clear dependency injection chains using FastAPI's `Depends` to supply the repository to the service, keeping the controller layer extremely lean.

**Any correction I had to make:**
- In `refresh`, I had to make sure we parse the `sub` token claim to `int` safely as JWT claims are strictly strings and the user repository expects an integer ID.
- **CSRF Protection via SameSite**: Originally used `samesite="lax"` for auth cookies, but as pointed out, this could conflict with robust CSRF protection in strict single-origin APIs. Upgraded cookie settings to use `samesite="strict"` to ensure cookies are never sent in cross-site requests, mitigating CSRF vulnerabilities completely for same-site clients.

## API Layer (Auth Routers)
**Prompt used:**
> In backend/app/api/routers/auth.py implement these endpoints: POST /api/auth/login, POST /api/auth/logout, POST /api/auth/refresh, GET /api/auth/me. Routers must be thin — no business logic, only call AuthService methods. Register the router in app/main.py with prefix /api/auth. Update AI_LOG and README.

**What AI decided and why:**
- **Thin Routers (`app/api/routers/auth.py`):** Created the requested endpoints ensuring absolutely zero business logic resides in the controller. The router merely injects dependencies (`AuthService` and optionally `current_user`), maps the HTTP request (JSON body, headers, cookies), and returns the service output.
- **`get_current_user` Dependency:** Added this extra dependency to `app/api/dependencies/core.py` to extract and decode the `access_token` cookie, which is necessary to inject the `current_user` into the `/me` endpoint.
- **FastAPI Registration (`app/main.py`):** Scaffolded a proper `FastAPI` application instance and registered the auth router with the `/api/auth` prefix.
- **Schema update (`app/schemas/user.py`):** Added a `UserLogin` Pydantic model so that `/login` safely validates incoming JSON containing email and password.

**Any correction I had to make:**
- **EmailStr in UserLogin:** Corrected the `UserLogin` schema to use `EmailStr` instead of `str` for the email field, ensuring incoming login requests are strictly validated before reaching the service layer.
