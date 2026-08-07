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
- Dependency injection (`app/api/dependencies/core.py`, `app/api/dependencies/auth.py`)
- API Auth Routers (`app/api/routers/auth.py`, `app/main.py`)
- Admin Users Router (`app/api/routers/users.py`)
- Hardware Layer (`app/repositories/hardware.py`, `app/services/hardware.py`)
- Hardware Router (`app/api/routers/hardware.py`)
- Rental Layer (`app/repositories/rentals.py`, `app/services/rentals.py`)
- Rental Router (`app/api/routers/rentals.py`)
- Audit Layer (`app/repositories/audit.py`, `app/services/audit.py`)
- Custom exception handling (`app/exceptions/auth.py`, `app/exceptions/users.py`)
- Unit and integration test suite (`tests/` with 99% coverage)

## Shortcuts
* **Users:** Registration, profile retrieval.
* **Hardware Inventory:** Full CRUD for IT Admins.
* **Rentals:** Renting devices, returning devices (automatically updating hardware statuses).
* **Audit System (AI-ready):** A reporting engine that flags potential inventory issues, preparing the codebase for a future AI/LLM integration.
* **Frontend:** Vue 3, TypeScript, Vite, Vue Router, Pinia, Axios.
* **Type Safety:** Shared TypeScript interfaces matching the backend Pydantic schemas for end-to-end safety.
* **Secure Auth (HttpOnly):** Automated Axios interceptors handle seamless background JWT token refreshing without exposing tokens to JavaScript. Pinia composition API store handles the UI authentication state (`user`, `isAdmin`).
* **Router Security:** Vue Router global `beforeEach` guards ensure protected routes (`/`, `/rentals`, `/admin`) verify authorization on navigation, dynamically fetching user sessions on load.
* **Global Notifications:** Pinia composition API Toast Store for standardized, auto-dismissible user feedback messages across the UI.
* **API Service Layer:** Isolated API wrapper functions (`hardware.ts`, `rentals.ts`, `audit.ts`) neatly map to FastAPI endpoints, returning fully typed TypeScript responses and throwing errors upward for Vue components to handle seamlessly.
* **Shared UI Architecture:** Reusable Vanilla CSS components (`AppNavbar`, `AppToast`, `StatusBadge`) providing dynamic layout, role-based navigation rendering, and visual state representation for the entire application.
* **Authentication UI:** A highly polished, dynamic `LoginView` offering responsive error handling and redirection, seamlessly integrated with the Pinia Auth Store and Axios interceptors.
* **Inventory Dashboard:** A robust `DashboardView` with real-time server-side pagination, sorting, status filtering, and one-click hardware renting wrapped in a modern, dark-themed glassmorphism UI.
* **User Rentals Management:** A dedicated `MyRentalsView` enabling users to view their active and past hardware rentals with one-click return functionality and historical date tracking.