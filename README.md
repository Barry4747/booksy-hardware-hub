# Booksy Hardware Hub

An internal tool for Booksy employees to manage, rent, and maintain company equipment.

---

## Setup

### Prerequisites
- Python 3.12+
- Node.js 18+
- [uv](https://docs.astral.sh/uv/) (Python package manager)

### Backend

```bash
cd backend
uv sync --dev
cp .env.example .env
# Fill in SECRET_KEY, GEMINI_API_KEY, and other values in .env
uv run python create_admin.py
uv run python -m app.db.seed
uv run uvicorn app.main:app --reload
```

API available at: `http://localhost:8000`
Interactive docs at: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
# Set VITE_API_BASE_URL=http://localhost:8000 in .env
npm run dev
```

App available at: `http://localhost:5173`

### Run Tests

```bash
cd backend
uv run pytest -v --cov=app
```

### Environment Variables

**Backend `.env`:**
```
SECRET_KEY=your-secret-key-min-32-chars   # generate: openssl rand -hex 32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
DATABASE_URL=sqlite:///./hardware_hub.db
GEMINI_API_KEY=your-gemini-api-key
AUDIT_RATE_LIMIT=5
ADMIN_EMAIL=admin@booksy.com
ADMIN_PASSWORD=your-admin-password
```

**Frontend `.env`:**
```
VITE_API_BASE_URL=http://localhost:8000
```

---

## Live Demo

> https://booksy-hardware-hub-umber.vercel.app/

---

## Implementation Status

### Fully Implemented

**Backend**
- SQLite database with strict foreign key enforcement via SQLAlchemy event listener (`PRAGMA foreign_keys=ON`)
- SQLAlchemy models: User, Hardware, Rental with proper relationships, cascade rules, and indexes
- Pydantic v2 schemas with `ConfigDict(from_attributes=True)` throughout
- Seed script with anomaly detection and structured logging — detects all 8 anomalies in the provided dataset
- Admin creation script with interactive prompt and env variable support
- JWT authentication using HttpOnly + SameSite=Strict cookies (access + refresh tokens)
- Full layered architecture: Routers -> Services -> Repositories with strict Unit of Work pattern (flush in repos, commit in services)
- Single shared SQLAlchemy Session per request — no session injection leaks
- Auth endpoints: login, logout, refresh, me
- User management: admin-only creation and deletion with force-return cascade logic
- Hardware CRUD with server-side pagination, filtering, and sorting
- Rental engine with strict one-way state machine: Available -> In Use -> Available
- Hardware status transition guards (cannot set In Use directly; cannot set Repair with active rental)
- Hardware deletion guard (cannot delete hardware with an active rental)
- User deletion guards (cannot delete last admin; cannot delete own account)
- AI Inventory Auditor powered by gemini-3.6-flash, async via `run_in_threadpool`
- Rate limiting on audit endpoint via `slowapi` (configurable via `AUDIT_RATE_LIMIT`)
- N+1 query elimination via `joinedload` on all rental queries
- Custom exception hierarchy with global FastAPI exception handlers
- Specific JWT exception handling (`ExpiredSignatureError`, `JWTError`) with debug logging
- 105 tests, 96% coverage

**Frontend**
- Vue 3 + TypeScript + Vite + Pinia + Axios
- TypeScript interfaces matching backend Pydantic schemas exactly
- Axios instance with `withCredentials: true` and concurrency-safe 401 interceptor (isRefreshing lock + subscriber queue)
- Auth Pinia store (Composition API) — no tokens in JS, HttpOnly cookies only
- Vue Router with `beforeEach` guards using `requiresAuth` and `requiresAdmin` meta fields
- Global Toast notification store with 3s auto-dismiss
- Isolated API service layer: `hardware.ts`, `rentals.ts`, `audit.ts`, `users.ts`
- Smart Layout system: separate `DesktopLayout` and `MobileLayout` via `AppLayout` component
- Hamburger navigation for mobile with animated overlay and route-change auto-close
- LoginView with double-submission protection and toast error feedback
- DashboardView with server-side pagination, filtering, sorting, and per-item rent protection (double-click guard via `rentingIds` Set)
- Pagination resets to page 1 on filter/sort change
- MyRentalsView with active/returned history and admin toggle to view all system rentals
- AdminView with tabbed interface: Hardware CRUD, User Management, AI Audit
- Direct navigation from audit issue cards to hardware edit view
- Role-based navigation (Admin Panel link visible to admins only)
- UI guard: Toggle Repair button disabled when hardware is In Use
- Purchase date field in hardware add/edit form
- Fully responsive — tested on 360px+ viewports

### Shortcuts & Hacks

- **SQLite over PostgreSQL**: Used SQLite for portability and ease of review without infrastructure setup.
  *Why OK:* Single-writer workload, no true concurrent writes in this MVP.
  *Future:* PostgreSQL + asyncpg + async SQLAlchemy for production scale and row-level locking (`SELECT ... FOR UPDATE`).

- **In-memory rate limiting (slowapi)**: Rate limit counter resets on every server restart.
  *Why OK:* Demo environment, single process.
  *Future:* Redis-backed rate limiting (slowapi supports this natively) for distributed deployments.

- **No email verification on user creation**: Admins create accounts directly with a password.
  *Why OK:* Internal corporate tool — admins control who has access.
  *Future:* Invite-based flow with email verification and self-serve password reset.

- **File-based SQLite database**: Database is a local `.db` file, not a managed service.
  *Why OK:* Required by the assignment brief for portability and ease of review.
  *Future:* Managed PostgreSQL (e.g. RDS, Supabase) for persistence, backups, and connection pooling.

### Partial / Missing

- No user profile update endpoint — users cannot change their own email or password.
  Intentional for this scope: credentials are admin-managed in a corporate inventory tool.
- No pagination on MyRentalsView — acceptable given typical rental volume per user.
- AdminView.vue exceeds the 200-line component guideline (~850 lines).
  Should be refactored into `HardwareTab.vue`, `UsersTab.vue`, `AuditTab.vue` sub-components.

### Next Steps (24h Roadmap)

1. Split AdminView.vue into focused tab sub-components to reduce component size
2. Migrate to PostgreSQL database
3. Use redis for caching and rate limiting

---

## AI Development Log

See [AI_LOG.md](./AI_LOG.md) for the full prompt trail, architectural decisions, and corrections made during AI-assisted development.