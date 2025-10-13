# Sales.recpires — Architecture & Documentation

This document explains the architecture, key components, setup instructions, testing guidance, migration steps, and troubleshooting tips for the Sales.recpires project.

Table of contents
- Project overview
- Repository layout
- High-level architecture
- Backend (Django + DRF)
  - Models
  - Serializers & Views
  - Order creation and stock handling
  - Management commands (data migration)
  - Admin setup
- Frontend (React + TypeScript + Vite)
  - Components overview
  - State management (CartContext)
  - API layer and error handling
  - Tests
- Setup & local development
  - Backend
  - Frontend
- Running tests
- Data migration
- Deployment notes
- Troubleshooting & common issues
- Next steps & improvements

---

## Project overview

Sales.recpires is a small e-commerce prototype with a Django backend (Django REST Framework) and a React + TypeScript frontend (Vite). The project supports:
- Products with optional per-product SKU
- Product variants (`ProductVariant`) with their own SKU, price and stock
- Orders and order items that reference variants when available
- Transactional order creation with atomic stock decrement
- Management command to migrate existing products into variants
- Frontend cart with variant selection, persisted to localStorage, and checkout flow that surfaces API validation errors

## Repository layout

- `backend/` — Django project and app code
  - `core/` — Django project settings and ASGI/WGSI
  - `sales/` — application: models, serializers, views, admin, management commands, tests
- `frontend/` — React + TypeScript UI built with Vite
  - `src/` — source files: components, pages, services, context, hooks, tests

## High-level architecture

- The frontend communicates with the backend REST API (DRF). Axios is used on the client with an interceptor to normalize API errors into a consistent shape.
- The backend exposes endpoints for products, variants, stores, orders and user-related actions.
- Inventory updates are performed in a database transaction and use `select_for_update` to lock variant rows and avoid race conditions.
- A management command helps migrate existing product-level stock/sku into variant rows.

## Backend (Django + DRF)

Key concepts and files:
- `backend/sales/models.py`
  - `Product` (catalog-level info)
  - `ProductVariant` (sku, price, stock, color, size, image, is_active)
  - `Order` and `OrderItem` (OrderItem may reference `ProductVariant`)

- `backend/sales/serializers.py`
  - `ProductSerializer`, `ProductVariantSerializer`
  - `OrderCreateSerializer` ensures orders decrement stock atomically and raises DRF `ValidationError` when insufficient stock.

- `backend/sales/admin.py`
  - Registers `ProductVariant` and updates `ProductAdmin`/`Order` admin UI.

- `backend/sales/management/commands/migrate_products_to_variants.py`
  - Command to migrate product fields into `ProductVariant` rows with flags for dry-run and SKU resolution strategies.

Order creation & stock handling
- Orders are created inside a `transaction.atomic()` context.
- For each item, the code resolves the variant (if provided) and uses `select_for_update()` to lock the variant row, checks stock and decrements it.

## Frontend (React + TypeScript + Vite)

Key concepts and files:
- `frontend/src/services/api.ts` — Axios instance with interceptors to normalize API error payloads to `error.apiErrors`.
- `frontend/src/services/errorUtils.ts` — helpers to extract friendly messages from server errors.
- `frontend/src/context/CartContext.tsx` — Cart provider stored in localStorage; stores `CartItem` including a `variantSnapshot` to make checkout fast and resilient.
- `frontend/src/components/common/ApiErrorAlert.tsx` — component that displays API errors using Ant Design `Alert`.
- Product listing & selection
  - `ProductCard.tsx` supports opening a modal to choose a variant and quantity. It dispatches to CartContext with `variantSnapshot` (sku/price/image).
- Checkout flow
  - `CheckoutPage.tsx` builds an order payload from cart items and calls `orderService.createOrder()`. API errors are displayed with `ApiErrorAlert`.

Tests
- Vitest + Testing Library are configured for unit tests.
- Tests added: `frontend/src/__tests__/ApiErrorAlert.test.tsx` and `CheckoutPage.test.tsx`.

Diagrams
-------
PlantUML diagrams are included under `docs/diagrams/`:

- `docs/diagrams/system.puml` — high-level system overview (frontend/backend/db/storage)
- `docs/diagrams/components.puml` — component-level diagram (frontend components and backend serializers/models)
- `docs/diagrams/order_flow.puml` — sequence diagram for order creation and stock decrement

Render instructions
-------------------
To render PNG/SVG locally you can use:

1. PlantUML (CLI) — requires Java and PlantUML:

```powershell
# Example (Windows PowerShell)
choco install plantuml -y   # or install manually
plantuml docs\diagrams\system.puml
```

2. VSCode PlantUML extension — open the `.puml` file and click preview, then export PNG/SVG.

3. Online PlantUML server — paste the content into https://www.planttext.com/ or use a PlantUML Docker container.

CI rendering
------------
There is a GitHub Actions workflow that will render the PlantUML files automatically on push/PR and upload the generated PNGs as an artifact. Workflow path: `.github/workflows/render-diagrams.yml`.
When the workflow runs, check the `Artifacts` section of the workflow run and download the `diagrams` artifact (PNG files are placed under `docs/diagrams/generated`).

Local helper scripts
--------------------
Two helper scripts are provided to render all diagrams locally using Docker:

- PowerShell: `scripts\render-diagrams.ps1`
- Bash: `scripts/render-diagrams.sh`

Usage (PowerShell):

```powershell
pwsh scripts\render-diagrams.ps1
```

Usage (bash):

```bash
./scripts/render-diagrams.sh
```

The generated PNG files are saved to `docs/diagrams/generated`.


## Setup & local development

Prerequisites
- Python 3.11+ (recommended) and `pip`
- Node.js 18+ and npm

Backend
1. Create and activate a virtual environment (PowerShell):

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Configure `.env` or environment variables as needed (database URL, secret key, AWS credentials if using S3, etc.).
3. Create and apply migrations:

```powershell
python manage.py makemigrations
python manage.py migrate
```

4. Create a superuser for admin access:

```powershell
python manage.py createsuperuser
```

Frontend
1. Install dependencies:

```powershell
cd frontend
npm install
```

2. Run dev server:

```powershell
npm run dev
```

3. Run tests:

```powershell
npm test
```

## Running tests
- Backend unit tests:
  - `python manage.py test` (run inside the activated backend virtualenv)
- Frontend unit tests:
  - `npm test` (requires Node and dev dependencies installed)

## Data migration (migrate_products_to_variants)

- Dry-run first to preview changes:
  - `python manage.py migrate_products_to_variants --dry-run`
- SKU resolution policy options: `append-id`, `skip`, `fail`.
  - Example: `python manage.py migrate_products_to_variants --resolve-skus=append-id`
- After verifying dry-run, run without `--dry-run`. Consider `--clear-product-fields` to remove SKU/stock from the product row if desired.

## Deployment notes
- Backend: typical WSGI/ASGI deployment (Gunicorn + HTTPS reverse proxy). `requirements.txt` lists production dependencies.
- Frontend: build with `npm run build` and serve static files (Vite preview or static hosting). Alternatively integrate build into Django static files pipeline or serve via CDN.

## Troubleshooting & common issues
- Import/type errors in editor: install packages locally (`pip install -r requirements.txt` and `npm install`) so language servers can resolve modules.
- TypeScript/JSX errors: ensure `tsconfig.json` has correct jsx setting (e.g. `"jsx": "react-jsx"`) and `@types/react` matching React version.
- Tests failing after migrations: ensure correct DB state and run management commands with `--verbosity` for debugging.

## Next steps / improvements
- Add E2E tests (Cypress / Playwright) for checkout and migration flows.
- Add GitHub Actions CI to run backend and frontend tests on push/PR.
- Add UI pages: order success/summary, order history.
- Harden concurrency: add integration tests to simulate concurrent orders.

---

If you want, I can now:
- Create a `README.md` with setup snippets and shortcuts (I recommend this next), and/or
- Add a `docs/` folder with architecture diagrams (PlantUML) and a GitHub Actions workflow to run tests.

Which should I generate next? (README.md, CI workflow, or PlantUML diagrams)