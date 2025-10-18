# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack sales management application with Django REST backend and React TypeScript frontend. Features JWT authentication, product/order management, and a component-based UI architecture.

## Technology Stack

**Backend (Django)**
- Django 5.2.6 with Django REST Framework 3.16.1
- JWT authentication via djangorestframework-simplejwt
- PostgreSQL database
- CORS enabled for local development (ports 3000, 5173, 5174)
- Environment variables managed via python-decouple

**Frontend (React)**
- React 19.1.1 with TypeScript
- Vite 7.1.7 for build tooling
- React Router DOM for navigation
- Axios for API calls with automatic token refresh
- Tailwind CSS for styling

## Development Commands

### Docker Setup (Recommended)

```bash
# Start PostgreSQL and pgAdmin via Docker
docker-compose up -d

# Check containers status
docker-compose ps

# Stop containers
docker-compose down

# Stop and remove volumes (WARNING: deletes all data)
docker-compose down -v
```

**Docker Services:**
- **PostgreSQL**: `localhost:5432`
  - Database: `sales_db`
  - User: `postgres`
  - Password: `postgres123`

- **pgAdmin** (Web UI): `http://localhost:5050`
  - Email: `admin@admin.com`
  - Password: `admin`

**Connecting DBeaver to Docker PostgreSQL:**
1. Open DBeaver
2. New Database Connection → PostgreSQL
3. Connection settings:
   - Host: `localhost`
   - Port: `5432`
   - Database: `sales_db`
   - Username: `postgres`
   - Password: `postgres123`
4. Test Connection → Finish

### Backend (Django)

```bash
# Activate virtual environment
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables (already configured for Docker)
cp .env.example .env

# Database migrations
python3 manage.py makemigrations
python3 manage.py migrate

# Create superuser for admin access
python3 manage.py createsuperuser

# Run development server
python3 manage.py runserver  # Runs on http://localhost:8000

# Access Django admin
# Navigate to http://localhost:8000/admin/

# Generate model diagram (requires django-extensions)
python3 manage.py graph_models sales -o models.png
```

### Frontend (React)

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev  # Runs on http://localhost:5173

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Architecture

### Backend Structure

**Django Apps:**
- `core/` - Main project settings, URLs, WSGI/ASGI configuration
- `sales/` - Sales app containing all business logic

**Sales App Components:**
- `models.py` - Product, Order, OrderItem models
- `serializers.py` - DRF serializers for API responses
- `views.py` - ViewSets for Product, Order, OrderItem (CRUD operations)
- `auth_views.py` - Authentication endpoints (register, login, logout, profile, change password)
- `auth_serializers.py` - Serializers for auth operations
- `urls.py` - API route definitions with DRF router
- `admin.py` - Django admin configuration

**API Endpoints:**
All endpoints are prefixed with `/api/` (defined in `core/urls.py`)

```
/api/products/              - Product CRUD (ViewSet)
/api/orders/                - Order CRUD (ViewSet)
/api/order-items/           - OrderItem CRUD (ViewSet)
/api/auth/register/         - User registration
/api/auth/login/            - JWT token generation
/api/auth/logout/           - Token blacklist
/api/auth/token/refresh/    - Refresh JWT token
/api/auth/profile/          - User profile
/api/auth/change-password/  - Password change
```

**Authentication Flow:**
- JWT tokens with 1-hour access token and 7-day refresh token
- Tokens rotate on refresh with automatic blacklisting
- Bearer token authentication in headers

**Data Models:**
- `Product` - name, description, SKU, price, stock, is_active, timestamps
- `Order` - customer info (name, email, phone, address), status, total_amount, timestamps
  - Status choices: pending, processing, shipped, delivered, cancelled
- `OrderItem` - links Product to Order with quantity and unit_price

### Frontend Structure

**Directory Layout:**
```
src/
├── components/
│   ├── aside/      - Sidebar components
│   ├── common/     - Reusable UI components (Button, Input, Card, Badge)
│   ├── layout/     - Layout components (Layout, Header)
│   └── navbar/     - Navigation bar components
├── pages/          - Route-level components (HomePage, LoginPage)
├── services/       - API client and service layer
│   ├── api.ts          - Axios instance with interceptors
│   ├── authService.ts  - Authentication methods
│   └── productService.ts - Product API calls
└── App.tsx         - Main app with routing and auth state
```

**API Client Configuration:**
- Base URL: `VITE_API_URL` env var or `http://localhost:8000/api`
- Automatic JWT token injection via request interceptor (frontend/src/services/api.ts:15)
- Automatic token refresh on 401 errors via response interceptor (frontend/src/services/api.ts:35)
- Tokens stored in localStorage (access_token, refresh_token, user)
- Path alias: `@/` maps to `src/` directory

**Authentication Flow:**
- `App.tsx` manages global auth state and route protection
- `authService.ts` provides login, logout, isAuthenticated, getCurrentUser methods
- Protected routes redirect to login if not authenticated
- Custom `auth-change` event triggers auth state updates across components

**Component Organization:**
- Common components export via index.ts barrel files
- Functional components with TypeScript interfaces
- Tailwind CSS for styling

## Important Notes

### Backend
- Virtual environment (`backend/venv/`) is committed but may need reinstallation
- CORS is configured for local development only - update `CORS_ALLOWED_ORIGINS` in `core/settings.py` for production
- Environment variables are managed via `.env` file (see `.env.example` for template)
- PostgreSQL database configuration via environment variables (DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
- Ensure PostgreSQL is installed and running before starting the application
- REST Framework uses pagination (10 items per page)

### Media Files (Product Images)
**Local Development:**
- Images are stored in `backend/media/` directory
- Django serves media files automatically via `/media/` URL
- No additional configuration needed

**Production (Two Options):**

**Option 1: AWS S3 (Recommended for production)**
1. Create an S3 bucket on AWS
2. Create IAM user with S3 access permissions
3. Set environment variables in production:
   ```
   USE_S3=True
   AWS_ACCESS_KEY_ID=your-access-key
   AWS_SECRET_ACCESS_KEY=your-secret-key
   AWS_STORAGE_BUCKET_NAME=your-bucket-name
   AWS_S3_REGION_NAME=us-east-1
   ```
4. Images will be automatically uploaded to S3
5. API returns full S3 URLs (e.g., `https://bucket.s3.amazonaws.com/media/products/image.jpg`)

**Option 2: Django/WhiteNoise (Simpler but not ideal)**
1. Set `USE_S3=False` in production environment
2. Ensure `MEDIA_ROOT` directory is writable
3. Note: Media files may be lost on server restarts (ephemeral filesystem on platforms like Render/Heroku)
4. Best for development/testing only

**Image URLs:**
- Backend serializers return absolute URLs using `request.build_absolute_uri()`
- Frontend renders images directly from API response
- Product images: `ProductSerializer.image` field
- Variant images: `ProductVariantSerializer.image` field

### Frontend
- Environment variable `VITE_API_URL` can override default API URL
- Token refresh happens automatically - handle logout on refresh failure
- Auth state syncs via localStorage events and custom `auth-change` event
- Vite dev server proxies API requests to avoid CORS issues in development

### Development Workflow
1. Start Docker containers: `docker-compose up -d`
2. Start backend server: `cd backend && python3 manage.py runserver`
3. Start frontend server: `cd frontend && npm run dev`
4. Create/apply migrations after model changes
5. Frontend watches for file changes and hot-reloads

### Docker Commands Reference
```bash
# View container logs
docker-compose logs -f postgres
docker-compose logs -f pgadmin

# Access PostgreSQL shell
docker exec -it sales_postgres psql -U postgres -d sales_db

# Backup database
docker exec -t sales_postgres pg_dump -U postgres sales_db > backup.sql

# Restore database
docker exec -i sales_postgres psql -U postgres sales_db < backup.sql

# Remove all containers and volumes
docker-compose down -v
```

## Project Guidelines (from claude.md)

The existing `claude.md` file contains Portuguese guidelines specifying:
- Use Ant Design for UI components (NOT Material-UI)
- Use React Query for async data management
- Use React Hook Form with Zod validation for forms
- Use React Spring for animations
- Functional components with TypeScript
- Tailwind CSS utility-first styling
- Component files should be max 200 lines
- Extract complex logic into custom hooks