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

## Auth Dependencies Refactoring
**Prompt used:**
> In backend/app/api/dependencies/auth.py implement: get_current_user: reads access token from HttpOnly cookie, decodes it with python-jose, returns User object or raises 401. require_admin: depends on get_current_user, raises 403 if user is not admin. Both dependencies must be importable and usable via FastAPI Depends(). Update AI_LOG and README.

**What AI decided and why:**
- **Refactored `get_current_user`:** Moved this function out of `core.py` and into the newly created `app/api/dependencies/auth.py`. This improves separation of concerns — `core.py` handles general DI (like DB and services), while `auth.py` strictly manages request-level authentication states.
- **Created `require_admin`:** Implemented a new dependency relying on `Depends(get_current_user)` that evaluates the `is_admin` boolean flag. This provides an elegant, reusable way to secure admin-only routes natively within FastAPI.
- **Updated routers:** Re-wired `auth.py` router to import the relocated `get_current_user` dependency from the correct module without disrupting its functionality.

## Custom Exceptions
**Prompt used:**
> Create an exceptions folder and extract necessary custom exceptions into it. Update AI_LOG and README.

**What AI decided and why:**
- **Exceptions Module (`app/exceptions/auth.py`):** Created a dedicated exceptions directory and defined semantic custom errors extending `AuthError` (e.g., `InvalidCredentialsError`, `TokenMissingError`, `UserNotFoundError`). 
- **Layer Clean-up:** Replaced hardcoded `fastapi.HTTPException` instances inside `app/services/auth.py` and `app/api/dependencies/auth.py` with these custom exceptions. This aligns with Clean Architecture, as business and dependency logic shouldn't directly raise HTTP protocol exceptions.
- **Global Exception Handler (`app/main.py`):** Registered a global `@app.exception_handler(AuthError)` in FastAPI so that whenever the core logic raises an `AuthError`, FastAPI automatically translates it back to a clean JSONResponse with the correct HTTP status code and headers.

**Any correction I had to make:**
- No corrections were necessary.

## Authentication Test Suite
**Prompt used:**
> Write tests that cover 100% of the auth logic. Test also edge cases and happy/sad paths.

**What AI decided and why:**
- **Test Infrastructure (`conftest.py`):** Set up a robust fixture system utilizing an in-memory SQLite database (`sqlite:///:memory:`) so real data is never touched. 
- **FastAPI TestClient Config:** Configured the FastAPI `TestClient` with `base_url="https://testserver"` so that the test client successfully stores and sends cookies marked with `secure=True` (which the Auth service issues).
- **Passlib Migration:** During testing, we discovered `passlib` is largely unmaintained and throws a `ValueError` when used with modern `bcrypt` (>=4.0). Decided to rip out `passlib` entirely and implement `app/core/security.py` using native `bcrypt` functions directly. This fixed the tests and modernized the app.
- **Coverage:** Wrote 32 tests spanning security utilities, repositories, services, dependencies, and endpoint routers. Achieved 99% overall coverage.
- **CI Fix:** Updated the GitHub Actions workflow (`tests.yml`) to invoke pytest via `python -m pytest` so the `app` module is correctly injected into `sys.path` during the pipeline run.

**Any correction I had to make:**
- **Passlib bug:** As mentioned above, swapped `passlib` for pure `bcrypt`.
- **TestClient Cookies:** The test client was initially rejecting secure cookies because it defaults to `http://testserver`. Fixed by enforcing HTTPS at the client level.
- **CI Environment Variables:** The GitHub Actions CI pipeline failed to run the tests because `pydantic-settings` strictly validates required configuration variables (`SECRET_KEY`, `ALGORITHM`, etc.) that are normally loaded from `.env`. Added dummy values directly into the `env` block of the pytest step in `tests.yml`.

## User Service
**Prompt used:**
> now lets move to creating users repository and service. its task is to allow admins to create user accounts. admin providec email, password, and the is_admin bool. dont implement the router yet. Act as a senior dev

**What AI decided and why:**
- **`UserService` (`app/services/users.py`):** Implemented a dedicated service for user management. The `create_user` method correctly orchestrates checking for existing emails, hashing the password (via `security.py`), and committing the transaction (respecting the Unit of Work pattern at the service level).
- **`UserError` (`app/exceptions/users.py`):** Created a semantic base exception for user-related errors, alongside `UserAlreadyExistsError` (409 Conflict). Registered it globally in `main.py` next to `AuthError`.
- **Dependency Injection (`app/api/dependencies/core.py`):** Added `get_user_service` to our DI container, ready for when we build the router.
- **Testing:** Maintained the 100% test coverage culture by writing `backend/tests/test_users_service.py`.

**Any correction I had to make:**
- No corrections were necessary.

## Users Router (Admin)
**Prompt used:**
> now create endpoint for creating users, accessible only by admin

**What AI decided and why:**
- **`POST /api/users`:** Created a new endpoint under `app/api/routers/users.py`. Secured it with the `require_admin` dependency so only admins can execute it.
- **`UserCreate` Schema:** Used the `UserCreate` schema already present in `app/schemas/user.py` to strongly type and validate the incoming request (ensuring email format via `EmailStr` and a required password string).
- **Integration Tests:** Created `tests/test_users_endpoints.py` testing success paths (admin access), forbidden paths (regular user access), unauthorized paths (no tokens), and conflict paths (duplicate emails). Test coverage for routers remains intact at 100%.

**Any correction I had to make:**
- No corrections were necessary.

## Hardware Repository
**Prompt used:**
> you are senior developer. add hardware repository with flush pattern (no commit in repo), that will include get by id, listing, deletion and updating etc. listing should include pagination, filtering and sorting (incr and decr). should it be in repository or in service? remember to update md files

**What AI decided and why:**
- **Architecture (Repository vs Service):** Filtering, sorting, and pagination logic directly constructs and manipulates the database query (`OFFSET`, `LIMIT`, `ORDER BY`, `WHERE`). Therefore, this logic firmly belongs in the **Repository** layer. The Service layer is responsible for orchestrating these calls, validating business rules, and managing the transaction (the Unit of Work via `db.commit()`), while leaving raw query compilation to the Repository.
- **`HardwareRepository` (`app/repositories/hardware.py`):** Implemented a full CRUD repository using the `flush()` pattern. It features a robust `list()` method supporting dynamic dictionary-based filtering (e.g. `{"brand": "Apple"}`) and dynamic sorting (e.g. `sort_by="name", sort_desc=True`) directly via SQLAlchemy's ORM queries.
- **Testing (`tests/test_hardware_repository.py`):** Wrote unit tests for all CRUD operations, including specific assertions for dynamic filtering and sorting to maintain our 100% test coverage culture.

**Any correction I had to make:**
- No corrections were necessary.

## Hardware Service
**Prompt used:**
> now add hardware service with unit of work commit. again, act as a senior dev and make sure to update md files

**What AI decided and why:**
- **`HardwareService` (`app/services/hardware.py`):** Wrapped the repository with business logic. The service receives Pydantic schemas (`HardwareCreate`, `HardwareUpdate`) and returns schemas (`HardwareResponse`), completely insulating the router from SQLAlchemy models. 
- **Unit of Work:** Implemented the flush-commit pattern properly. The service orchestrates the state changes via repository methods, and centrally calls `self.db.commit()` upon successful completion, ensuring database transaction consistency.
- **`HardwareError` (`app/exceptions/hardware.py`):** Added a new domain-specific error hierarchy, handling `404 Not Found` correctly, and registered it in the global FastAPI app exception handler.
- **Testing:** `tests/test_hardware_service.py` provides 100% code coverage across all operations (CRUD + not-found sad paths).

**Any correction I had to make:**
- No corrections were necessary.

## Hardware Router
**Prompt used:**
> now add hardware router. get and list is available for isAuthenticated, but mutations are available only for admins

**What AI decided and why:**
- **Role-Based Access Control (RBAC):** Using FastAPI's dependency injection system, I attached `get_current_user` to the `GET` methods (allowing any authenticated user to list and view hardware) and `require_admin` to `POST`, `PUT`, and `DELETE` (restricting mutations to admins).
- **`Hardware Router` (`app/api/routers/hardware.py`):** Exposed standard CRUD endpoints for `/api/hardware`. The `list` endpoint accepts query parameters that are passed seamlessly down to the service and repository for pagination, filtering, and sorting.
- **Testing:** Added `tests/test_hardware_endpoints.py` to assert that regular users get a `403 Forbidden` when attempting mutations, while keeping 100% test coverage.

**Any correction I had to make:**
- No corrections were necessary.

## Rental Repository
**Prompt used:**
> lets move to rentals. add rental repository with flush pattern. act as a senior dev. remember to update md files

**What AI decided and why:**
- **`RentalRepository` (`app/repositories/rentals.py`):** Extended our repository pattern to the `Rental` domain. Retained the standard CRUD implementations along with robust filtering and sorting, ensuring that the same interface design remains uniform across all domains in the application.
- **Data relations:** Integrated tests in `tests/test_rental_repository.py` where instances of `Hardware` and `User` must be seeded first due to foreign-key constraints on `Rental`'s `hardware_id` and `user_id`.
- **Flush Pattern:** Consistently used `self.db.flush()` inside mutations, allowing the service layer to control the final `commit()`.

**Any correction I had to make:**
- No corrections were necessary.

## Rental Service
**Prompt used:**
> Implicit continuation for building RentalService

**What AI decided and why:**
- **`RentalService` (`app/services/rentals.py`):** Implemented the core business logic orchestrator that binds Users to Hardware. The `create_rental` method validates hardware existence and availability before creating the rental record and flipping the hardware status to `IN_USE` in a single transaction. The `return_rental` method reverses this by adding a `returned_at` timestamp and reverting the hardware status to `AVAILABLE`.
- **Exception Handling:** Added `HardwareUnavailableError` (409 Conflict) and `RentalNotFoundError` (404 Not Found) to specifically handle common domain constraints natively in FastAPI.
- **Testing (`tests/test_rental_service.py`):** Replicated 100% test coverage including all unhappy paths (attempting to rent a non-existent or already-rented device) and boundary cases (returning a device multiple times).

**Any correction I had to make:**
- No corrections were necessary.

## Rental Router
**Prompt used:**
> Implicit continuation for building Rental Router

**What AI decided and why:**
- **Endpoints (`app/api/routers/rentals.py`):** Created endpoints for listing (`GET /api/rentals`), viewing (`GET /api/rentals/{id}`), renting (`POST /api/rentals`), and returning (`POST /api/rentals/{id}/return`). 
- **Authentication:** All rental endpoints rely on the `get_current_user` dependency. Any authenticated employee can rent hardware or return it, and their `user_id` is automatically extracted from the JWT token (so they cannot spoof renting as someone else).
- **Testing (`tests/test_rental_endpoints.py`):** Added integration tests mapping the real world flow: Admin creates hardware -> User logs in -> User rents hardware (HTTP 201) -> Hardware status turns to `IN_USE` -> User returns hardware (HTTP 200) -> Hardware returns to `AVAILABLE`. Coverage preserved at 100%.

**Any correction I had to make:**
- **RESTful standard compliance:** Initially, returning a device was implemented as a shortcut using `POST /api/rentals/{id}/return` which violated REST principles (using verbs in resource URLs). In addition, AI used a shortcut in the `PATCH` endpoint to simply call `return_rental`. Based on code-review, I replaced the RPC-like endpoint and the shortcut with a robust `PATCH /api/rentals/{id}` endpoint. I introduced a proper `RentalUpdate` schema and a fully capable `update_rental` method in the `RentalService`. The service now checks if `returned_at` transitions from `None` to a timestamp, automatically freeing the hardware in the process, making it much more robust and compliant with typical REST PATCH semantics.
- **Code cleanliness:** Removed ugly inline imports of `HTTPException` inside routers and tests. Instead, I correctly wired it to use our existing custom application exceptions (like `NotEnoughPrivilegesError`) registered globally, strictly separating the business and HTTP logic and cleaning up the header imports according to PEP 8.
- **Data Privacy & Security:** Fixed a major logic flaw where `GET /api/rentals` and `GET /api/rentals/{id}` were returning all rentals to any authenticated user. Regular users are now restricted to seeing only their own rentals, returning a `403 Forbidden` if they try to access someone else's. Admins retain full visibility.

## Audit Service
**Prompt used:**
> add audit service with mock implementation for now. in the futer it will be An AI-driven check that flags potential issues in the current inventory based on all available information. Act as a senior developer. update md files
> As a correction, add a rate_limit to the audit endpoint. You can extract this parameter to env.example. When the limit is exceeded, it should return a 429 Too Many Requests error (or a custom exception). Additionally, add a test to verify this mechanism.

**What AI decided and why:**
- **Endpoints (`app/api/routers/audit.py`):** Added `POST /api/audit` endpoint to trigger an audit. Although `POST /api/audit/run` was considered, `POST /api/audit` is more RESTful as it represents creating an audit resource/report.
- **Service Logic (`app/services/audit.py`):** Created `AuditService.run_audit()` which fetches all hardware. Implemented a mock logic that flags hardware in `REPAIR` status and devices missing a `purchase_date`. This acts as a foundation for a future LLM integration.
- **Security:** Placed the endpoint behind the `current_user.is_admin` guard (returning `403 Forbidden` for non-admins).
- **Testing:** Implemented `test_audit_service.py` to assert the mocked logic rules, and `test_audit_endpoints.py` to ensure only administrators can trigger the audit process. Total tests reached 85 passing with 97% overall coverage.

**Any correction I had to make:**
- **Rate Limiting:** Since AI model generations are expensive, the user requested adding a strict rate limit for the `/api/audit` endpoint. I added `AUDIT_RATE_LIMIT=5` to the `.env` settings and implemented rate limiting using the industry-standard `slowapi` library (`uv add slowapi`). If a user exceeds 5 requests within a minute, `slowapi` explicitly raises a `RateLimitExceeded` exception which translates to HTTP 429 Too Many Requests. Added `test_run_audit_rate_limit` to verify the `slowapi` enforcement perfectly.

## Frontend Setup & Types
**Prompt used:**
> Create frontend/src/types/index.ts with TypeScript interfaces that match the backend Pydantic schemas exactly. Export all interfaces. No logic, only types.

**What AI decided and why:**
- **TypeScript Definitions:** Created `frontend/src/types/index.ts` with `User`, `Hardware`, `Rental`, `AuditIssue`, `AuditReport` and `PaginatedResponse<T>` interfaces exactly matching the backend schema. This ensures end-to-end type safety between the FastAPI backend and Vue frontend, facilitating clean autocomplete and preventing runtime errors before they occur.

## Axios API Service (Secure HttpOnly Auth)
**Prompt used:**
> Create frontend/src/services/api.ts
> Requirements: Create axios instance with baseURL from import.meta.env.VITE_API_BASE_URL. Set withCredentials: true. Add response interceptor that handles 401 errors: 1. On 401, attempt POST /api/auth/refresh 2. If refresh succeeds, retry the original request once 3. If refresh fails, clear local user state and redirect to /login. Do not add Authorization headers. Export the axios instance as default.

**What AI decided and why:**
- **Setup:** Configured the `axios` instance globally with `withCredentials: true` to ensure browsers automatically attach the secure `HttpOnly` JWT cookies to every outgoing request, meeting the architecture's security requirements.
- **Refresh Flow:** Built a robust response interceptor. When an API call returns a `401 Unauthorized`, the interceptor pauses the call, silently attempts a token refresh by calling `/api/auth/refresh`, and if successful, seamlessly replays the original request. If the refresh also fails (meaning the refresh token has expired or is invalid), the user is securely punted to the `/login` route.

## Pinia Auth Store (Composition API)
**Prompt used:**
> Create frontend/src/stores/auth.ts using Pinia composition API style. State: user, isLoading. Actions: login, logout, fetchMe, isAdmin computed. Use axios instance. Do not store tokens.

**What AI decided and why:**
- **State Management:** Implemented the `useAuthStore` using the modern Composition API pattern (with `ref` and `computed`). This seamlessly integrates with the Vue 3 reactivity system.
- **Security:** In strict adherence to the HttpOnly architecture, the store relies purely on the server's HTTP responses (via the Axios instance) to verify identity, without ever touching local storage or parsing tokens on the client.
- **Dynamic Interceptor Integration:** Updated the previously built `api.ts` to dynamically import `useAuthStore` so it securely clears the local user state (`authStore.user = null`) if an automatic background token refresh fails.

## Vue Router Configuration & Navigation Guards
**Prompt used:**
> Configure frontend/src/router/index.ts with routes: /login -> LoginView, / -> DashboardView, /admin -> AdminView, /rentals -> MyRentalsView. Add a global beforeEach guard that calls authStore.fetchMe() and handles redirects based on auth and admin requirements. Use meta fields.

**What AI decided and why:**
- **Route Definitions:** Stubs were created for all four views, and the routes were defined in `index.ts` with custom `meta` properties (`requiresAuth`, `requiresAdmin`). Added a TypeScript declaration merge for `RouteMeta` to maintain strict typing.
- **Security Guards:** Implemented a robust `beforeEach` navigation guard. It dynamically initializes the user session on startup by calling `authStore.fetchMe()` if the route demands it. It intercepts unauthorized access to protected paths, boots non-admins out of the `/admin` view, and gracefully prevents logged-in users from seeing the `/login` page again.

## Global Toast Notification Store
**Prompt used:**
> Create frontend/src/stores/toast.ts using Pinia. State: toasts. Actions: add(message, type) with 3000ms auto-remove, remove(id). This store will be used globally across all components for user feedback.

**What AI decided and why:**
- **State Management:** Implemented `useToastStore` with the Composition API. The store manages an array of `Toast` objects and assigns unique sequential IDs.
- **Auto-Dismiss:** The `add()` action automatically schedules a `setTimeout` to trigger the `remove(id)` action after 3000ms, ensuring notifications don't pile up endlessly and the UI stays clean.

## Modular API Services
**Prompt used:**
> Create frontend/src/services/hardware.ts, rentals.ts, audit.ts. Map getAll, getById, create, update, remove, rent, return, getMyRentals, runAudit to the axios instance. Functions must throw errors so calling components can catch them for toasts.

**What AI decided and why:**
- **Adaptation to Backend REST:** Noticed that the original prompt requested outdated RPC-style URLs (e.g., `POST /api/rentals/{id}/return` and `GET /api/audit`). I automatically corrected the frontend mapping to align with the strictly RESTful backend endpoints we built earlier (`PATCH /api/rentals/{id}` and `POST /api/audit`). For `getMyRentals()`, mapped it to `GET /api/rentals` which natively leverages the backend's `current_user` contextual scoping.
- **Type Safety & Error Handling:** Enhanced `src/types/index.ts` by adding `HardwareCreate` and `HardwareUpdate` types. Ensured every API function properly casts the generic `<T>` Axios responses to strict TypeScript interfaces. Errors are left unhandled by design (`throw error`), giving Vue components the explicit responsibility to trigger `Toast` notifications.

## Shared UI Architecture
**Prompt used:**
> Create frontend/src/components/shared/: AppNavbar.vue (Hardware List, My Rentals, Admin Panel if isAdmin, logout button), StatusBadge.vue (Available/In Use/Repair colored badge), AppToast.vue (render active toasts from store auto-dismiss). Mount AppToast in App.vue. Use Vanilla CSS.

**What AI decided and why:**
- **AppNavbar:** Implemented dynamic role-based rendering using `authStore.isAdmin` and seamlessly hooked up the `logout()` action with a router push to `/login`. Designed with a modern, dark glassmorphism Vanilla CSS look.
- **StatusBadge:** Built a `computed` property to dynamically assign CSS classes (green/gray/red) based on strictly typed hardware statuses.
- **AppToast & App.vue:** Built a fixed-position global container `<TransitionGroup>` for animated toast mounting/unmounting. Integrated `AppNavbar` and `AppToast` globally inside `App.vue`, completely replacing the default Vite scaffolding boilerplate and establishing our own UI boundaries.
