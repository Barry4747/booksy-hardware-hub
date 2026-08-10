# AI Development Log

## Tooling

- **Antigravity IDE**: Primary IDE — used for pair programming throughout the entire project
- **Cloude Sonnet 4.6**: Architecture planning, refactoring sessions, and code review
- **gemini-3.6-flash**: Inventory Auditor feature (via Google AI Studio API)

All major architectural decisions were made by me. AI was used to accelerate
implementation, not to replace judgment. Every AI-generated output was reviewed,
and corrections are documented below.

---

## Data Strategy

The provided seed dataset contained intentional anomalies designed to test data
handling. I identified all 8 before writing any code:

| ID | Anomaly | Detection Method | Action |
|----|---------|-----------------|--------|
| 4 (duplicate) | Duplicate primary key | In-memory `seen_ids` set | Skipped, logged |
| 6 | Purchase date in the future (2027) | Date comparison against `datetime.now()` | Inserted, flagged |
| 9 | Brand typo "Appel" | `difflib.get_close_matches` against known brands | Inserted, flagged |
| 9 | Wrong date format "22-05-2023" | Fallback date parser | Parsed, flagged |
| 10 | Missing brand | Empty string check | Inserted, flagged |
| 10 | Unknown status "Unknown" | `HardwareStatus` enum parsing | Skipped, flagged |
| 5 | Damage in notes, status Available | Keyword check on notes field | Inserted, flagged |
| 11 | Damage in history field, status Available | history -> notes migration + keyword check | Inserted, flagged |
| 7 | `assignedTo` present but no rental record | `assignedTo` stripped silently | Inconsistency surfaces via AI Audit only |

The seed is fully idempotent — running it multiple times produces the same database state.

---


## Prompt Trail

### Session 1 — Database Models and Schemas

**Prompt:**
> Create database models and Pydantic schemas for User, Hardware, Rental, Audit.
> Database setup in app/db/base.py. Use Pydantic v2 syntax. Hardware status must be
> a Python Enum. All models must have proper relationships defined.

**What AI decided:**
- Used `enum.Enum` for `HardwareStatus` — cleaner than string constants, validated at DB level
- Chose `ConfigDict(from_attributes=True)` over the deprecated `class Config` for all schemas
- Added base classes (`UserBase`, `HardwareBase`) to reduce schema duplication

**Corrections:**
- Agent used plain `str` for email fields to avoid adding a dependency. Added `email-validator`
  and switched to `EmailStr` — without it the API accepts malformed emails like "notanemail".
- Agent passed `datetime.now(timezone.utc)` directly as a column default, which evaluates
  once at import time, giving all records the same timestamp. Switched to `func.now()`.

---

### Session 2 — Seed Script and Admin Creation

**Prompt:**
> Create app/db/seed.py to load hardware seed data with anomaly detection and logging.
> Create create_admin.py. Make seed idempotent. Create empty seed_data.json.

**What AI decided:**
- All anomaly detection logic in `seed.py` rather than a separate validator — keeps the
  data flow in one place and produces a clean summary log on every run
- Used `difflib.get_close_matches` with `cutoff=0.7` for brand typo detection

**Corrections:**
- Agent only checked the database for duplicate IDs, missing duplicates within the seed
  file itself. Two records with `id:4` would both be added to the session (not yet
  committed) so the second DB query found nothing. Fixed with an in-memory `seen_ids` set.
- Agent placed `db.close()` outside the try/except. If commit raised, the session would
  leak. Wrapped in `try/except/finally`.
- Agent returned `None, False` for unrecognized date formats, silently discarding the
  anomaly. Fixed to return `None, True` so the anomaly counter increments.

---

### Session 3 — Security Utilities

**Prompt:**
> Implement password hashing and JWT token management in app/core/security.py using
> python-jose. Read config from pydantic-settings.

**What AI decided:**
- Used `python-jose` over `PyJWT` — better FastAPI ecosystem integration
- Separated access and refresh token creation into distinct functions with configurable
  expiry times read from settings

**Corrections:**
- Agent used `datetime.utcnow()` for token expiry, deprecated in Python 3.12+.
  Replaced with `datetime.now(timezone.utc)`.
- During test suite development, discovered `passlib` throws a `ValueError` with modern
  `bcrypt` (>=4.0) due to abandoned maintenance. Replaced `passlib` entirely with native
  `bcrypt` functions, modernizing the dependency.

---

### Session 4 — Auth Service and Repository

**Prompt:**
> Implement AuthService with login, logout, refresh, me using HttpOnly cookies.
> Repositories must use flush() only — commit belongs to the service layer.

**What AI decided:**
- HttpOnly + SameSite=Strict cookies over Authorization headers — tokens never accessible
  to JavaScript, eliminates XSS token theft entirely
- Strict flush/commit separation: repositories only write to the session, services own
  the transaction boundary (Unit of Work pattern)

**Corrections:**
- Initially used `samesite="lax"`. Upgraded to `samesite="strict"` for stronger CSRF
  protection since the API and frontend share the same origin in production.

---

### Session 5 — Hardware and Rental Layers

**Prompt:**
> Add hardware repository with pagination, filtering, sorting. Add hardware service with
> Unit of Work commit. Add rental repository and service with strict state machine guards.

**What AI decided:**
- Pagination, filtering, and sorting logic belongs in the Repository — it directly
  constructs the DB query. The Service only orchestrates and commits.
- Rental state machine: Available -> In Use (rent), In Use -> Available (return).
  No other transitions allowed through the rental engine.

**Corrections:**
- Initially implemented return as `PATCH /api/rentals/{id}` for REST compliance.
  After code review, this gave clients too much control over internal fields — a client
  could reset `returned_at` to null and reactivate a returned rental. Replaced with
  `POST /api/rentals/{id}/return` as a focused sub-resource action. Deliberate trade-off: slight
  REST convention deviation in exchange for strict server-side state machine enforcement.
- Fixed data privacy gap: `GET /api/rentals` was returning all rentals to any authenticated
  user. Regular users are now scoped to their own rentals via `current_user.id` filtering.
  Admins retain full visibility.

---

### Session 6 — Dependency Injection Architecture

**Prompt:**
> Fix the session injection bug in core.py — three separate Depends(get_db) calls
> were creating three independent Session objects.

**What AI decided:**
- Construct repositories inside service factory functions, all sharing the single `db`
  Session injected by FastAPI's dependency system.
- This guarantees writes in `HardwareRepository` and `RentalRepository` are in the same
  transaction and visible to each other before commit.

**The bug explained:**
```python
# BEFORE (broken) — three separate sessions
def get_rental_service(
    db: Session = Depends(get_db),               # Session A
    rental_repo = Depends(get_rental_repository), # Session B
    hw_repo = Depends(get_hardware_repository),   # Session C
) -> RentalService: ...

# AFTER (correct) — one shared session
def get_rental_service(
    db: Session = Depends(get_db),
) -> RentalService:
    rental_repo = RentalRepository(db)
    hw_repo = HardwareRepository(db)
    return RentalService(db=db, rental_repo=rental_repo, hw_repo=hw_repo)
```

---

### Session 7 — Status Transition Guards

**Prompt:**
> Block direct status mutation to In Use via hardware update. Block setting Repair
> when hardware has an active rental. Block deleting hardware with active rental.

**What AI decided:**
- Status transitions that bypass the rental state machine must be rejected at the
  service layer — business rules belong in services, not routers.
- Deletion with active rental is rejected (409) rather than force-closed — explicit
  admin action is safer than silent cascade.

---

### Session 8 — User Deletion Guards

**Prompt:**
> Prevent deleting the last admin. Prevent self-deletion. Implement delete_user
> with force-return of active rentals on deletion.

**What I decided:**
- Last-admin guard at the service layer: count admins before deletion, reject if <= 1
- Self-deletion guard at the router layer: compare `id` to `current_user.id`
- Force-return active rentals before deletion: sets `returned_at` and
  `hardware.status = AVAILABLE` atomically in the same transaction, then cascade
  removes the rental record with the user

**Corrections:**
- The `User` model was missing `cascade="all, delete-orphan"` on the rentals relationship.
  Without it, deleting a user with historical (returned) rentals threw `IntegrityError`.
  Added cascade before implementing the deletion logic.

---

### Session 9 — Gemini Inventory Auditor

**Prompt:**
> Replace mock audit with gemini-3.6-flash integration. Serialize hardware, send
> structured prompt, parse JSON response, handle markdown fences. Wrap in run_in_threadpool.

**Prompt sent to Gemini:**
```
You are an inventory auditor for a hardware management system.
Analyze the following hardware inventory and identify anomalies.

Return ONLY valid JSON in this exact format, no markdown, no explanation:
{
  "issues": [
    {
      "hardware_id": <int>,
      "hardware_name": "<str>",
      "severity": "<critical|warning|info>",
      "issue": "<short description>",
      "recommendation": "<what to do>"
    }
  ],
  "summary": "<one sentence overall assessment>"
}

Flag these issues:
- Purchase dates in the future
- Missing or empty brand names
- Possible brand name typos
- Items with damage mentioned in notes but status Available
- Items with status In Use but no active rental record
- Any other inconsistencies that would concern an IT manager

Inventory:
{inventory_json}
```

**What Gemini got right:**
- Correctly identified items with damage notes and Available status
- Correctly flagged missing purchase dates and empty brand names
- JSON structure was consistent and well-formed across multiple runs

**What Gemini missed / Corrections:**
- Consistently wrapped output in markdown fences despite explicit instructions not to.
  Added stripping logic before `json.loads()` — see "The Correction" section above.
- On API failure, the original implementation returned `200 OK` with an empty issues array.
  This caused the frontend to show nothing instead of an error toast. Refactored to raise
  `HTTPException(500)` on Gemini failure so the Axios interceptor triggers a red toast.
- The Gemini SDK is synchronous. Calling it inside an async FastAPI handler without
  offloading blocks the event loop for several seconds per audit. Wrapped in
  `run_in_threadpool` so the main event loop remains free during the API call.

---

### Session 10 — Frontend Architecture

**Prompt:**
> Set up Vue 3 + TypeScript + Vite. Add TypeScript interfaces, axios instance with
> withCredentials and 401 interceptor, Pinia auth store, Vue Router with guards,
> toast store, and API service layer.

**What I decided:**
- `withCredentials: true` on the axios instance — required for HttpOnly cookies on
  cross-origin requests during local development
- No tokens in JavaScript state — auth state validated server-side on every `fetchMe()`
- Service layer isolation: all API calls go through typed functions in `services/`,
  never directly from components

**Corrections:**
- Initial 401 interceptor fired multiple concurrent refresh requests when several API
  calls failed simultaneously on page load. Fixed with an `isRefreshing` lock and a
  subscriber queue at module level — only one refresh fires regardless of concurrent 401s:

```typescript
let isRefreshing = false
let refreshSubscribers: ((success: boolean) => void)[] = []

// First 401: set lock, attempt refresh, notify queue on completion
// Subsequent 401s: subscribe to queue, wait for first refresh to resolve
```

- `AdminView.vue` contained a direct `api.post('/api/users')` call bypassing the service
  layer. Extracted to `users.ts` `createUser()` function for consistency.

---

### Session 11 — Wireframe Implementation

**Context:** Provided Figma wireframe screenshot to Cursor as visual reference for the UI.

**What I decided:**
- Switched from dark glassmorphism to the light flat design from the wireframe
- Restructured `AppNavbar.vue` into a fixed left sidebar with SVG icons
- Kept all existing logic (store calls, service calls, event handlers) untouched —
  only HTML structure and scoped CSS were changed

**Corrections:**
- Agent initially rebuilt the entire `DashboardView` component, breaking several event
  handlers and `v-if` conditions. Instructed it to separate concerns: "Change only the
  template HTML structure and style scoped CSS. Do not touch script." Second pass was clean.

---

### Session 12 — Mobile Responsiveness

**Prompt:**
> Implement Smart Layout pattern with separate DesktopLayout and MobileLayout.
> Add hamburger navigation for mobile with animated overlay.
> Fix horizontal body scroll. Fix tables, toolbars, and forms for 360px+ viewports.

**What I decided:**
- Smart Layout pattern (`AppLayout.vue` switching between `DesktopLayout` and `MobileLayout`
  based on viewport width) rather than media-query-only CSS — cleaner separation of concerns
- Hamburger with full-screen overlay rather than bottom nav — more familiar for a web app
- Desktop layout left completely unchanged — mobile is additive, not a replacement

**Corrections:**
- Initial CSS-only approach converted the sidebar to a horizontal scrolling top bar on mobile.
  This caused links to overflow and overlap as seen in the screenshot. Replaced with a proper
  hamburger + full-screen overlay pattern using a new `MobileNavbar.vue` component.
- Added `watch(route, () => { isOpen.value = false })` to auto-close the menu on navigation
  — without this the overlay remained open after clicking a link or pressing browser back.

---

### Session 13 — Final Code Review and Bugfixes

Ran two comprehensive automated code reviews across the entire codebase. Key findings addressed:

- **SQLite foreign keys**: Added `PRAGMA foreign_keys=ON` event listener — SQLite does not
  enforce FK constraints by default
- **Transaction atomicity**: All multi-repository operations verified to share a single
  SQLAlchemy Session per request after the DI fix
- **Broad exception catching**: Replaced `except Exception` in `auth.py` with specific
  `ExpiredSignatureError` and `JWTError` catches, added `logger.debug` for diagnostics
- **Pagination desync**: Added `watch([statusFilter, sortBy, sortOrder], () => { page.value = 1 })`
  to reset pagination when filters change — without this, page 3 with a 1-page filter
  returned an empty "No hardware found" state
- **Missing purchase date field**: Added `<input type="date">` to the hardware add/edit form
  in `AdminView.vue` — without it, `purchase_date` always defaulted to `null`
- **UI guard**: Disabled Toggle Repair button when hardware is In Use to prevent
  guaranteed-to-fail API calls with a clear tooltip explaining why
- **Unused imports**: Removed unused `api` import from `AdminView.vue` and unused
  `computed` from `MyRentalsView.vue`
- **Test coverage**: Added missing tests for deleting In Use hardware, deleting last admin,
  self-deletion attempts, and status transition guard violations

## Tests and docs
In my prompts I also instructed AI to cover written code with tests, and also update docs. This helped me a lot, especially the test coverage part, it helped me to ensure that the code is working as expected and is well documented.

Final test count: 105 tests, 96% coverage.