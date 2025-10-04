# Sales Management System

A full-stack sales management application built with Django REST Framework and React TypeScript, featuring JWT authentication, product/order management, and a modern component-based UI architecture.

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Database Management](#database-management)
- [Development](#development)
- [License](#license)

## ✨ Features

- **User Authentication**
  - JWT-based authentication with token refresh
  - User registration and login
  - Password change functionality
  - Automatic token rotation with blacklisting

- **Product Management**
  - Create, read, update, and delete products
  - SKU tracking and inventory management
  - Product status control (active/inactive)

- **Order Management**
  - Complete order lifecycle management
  - Order status tracking (pending, processing, shipped, delivered, cancelled)
  - Customer information management
  - Order items with quantity and pricing

- **Modern UI**
  - Responsive design with Tailwind CSS
  - Component-based architecture
  - Protected routes with automatic redirection
  - Real-time authentication state management

## 🛠️ Technology Stack

### Backend
- **Django 5.2.6** - Web framework
- **Django REST Framework 3.16.1** - RESTful API
- **PostgreSQL** - Database
- **djangorestframework-simplejwt** - JWT authentication
- **python-decouple** - Environment variable management
- **Docker & Docker Compose** - Containerization

### Frontend
- **React 19.1.1** - UI library
- **TypeScript** - Type safety
- **Vite 7.1.7** - Build tool
- **React Router DOM** - Navigation
- **Axios** - HTTP client with interceptors
- **Tailwind CSS** - Styling

## 📦 Prerequisites

- Python 3.8+
- Node.js 16+
- Docker & Docker Compose
- Git

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd sales
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Optional: Configure API URL
# Create .env file with: VITE_API_URL=http://localhost:8000/api
```

### 4. Database Setup with Docker

```bash
# From project root, start PostgreSQL and pgAdmin
docker-compose up -d

# Verify containers are running
docker-compose ps
```

**Database Credentials:**
- **PostgreSQL**: `localhost:5432`
  - Database: `sales_db`
  - Username: `postgres`
  - Password: `postgres123`

- **pgAdmin**: `http://localhost:5050`
  - Email: `admin@admin.com`
  - Password: `admin`

### 5. Run Database Migrations

```bash
# From backend directory
cd backend
source venv/bin/activate

# Create and apply migrations
python3 manage.py makemigrations
python3 manage.py migrate

# Create superuser for admin access
python3 manage.py createsuperuser
```

## 🎯 Running the Application

### Start Backend Server

```bash
cd backend
source venv/bin/activate
python3 manage.py runserver
```

Backend will be available at: `http://localhost:8000`
- API Base URL: `http://localhost:8000/api`
- Admin Panel: `http://localhost:8000/admin`

### Start Frontend Server

```bash
cd frontend
npm run dev
```

Frontend will be available at: `http://localhost:5173`

## 📁 Project Structure

```
sales/
├── backend/
│   ├── core/                 # Django project settings
│   │   ├── settings.py      # Configuration
│   │   └── urls.py          # Main URL routing
│   ├── sales/               # Sales application
│   │   ├── models.py        # Data models (Product, Order, OrderItem)
│   │   ├── serializers.py   # DRF serializers
│   │   ├── views.py         # ViewSets for CRUD operations
│   │   ├── auth_views.py    # Authentication endpoints
│   │   └── urls.py          # API routes
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable components
│   │   │   ├── aside/       # Sidebar components
│   │   │   ├── common/      # UI components (Button, Input, Card)
│   │   │   ├── layout/      # Layout components
│   │   │   └── navbar/      # Navigation
│   │   ├── pages/           # Route-level components
│   │   ├── services/        # API client and services
│   │   │   ├── api.ts       # Axios instance with interceptors
│   │   │   ├── authService.ts
│   │   │   └── productService.ts
│   │   └── App.tsx          # Main app with routing
│   ├── package.json
│   └── vite.config.ts
│
├── docker-compose.yml       # Docker services configuration
├── CLAUDE.md               # Development guidelines
└── README.md               # This file
```

## 📚 API Documentation

### Authentication Endpoints

```
POST   /api/auth/register/         - User registration
POST   /api/auth/login/            - Login (get JWT tokens)
POST   /api/auth/logout/           - Logout (blacklist token)
POST   /api/auth/token/refresh/    - Refresh access token
GET    /api/auth/profile/          - Get user profile
PUT    /api/auth/profile/          - Update user profile
POST   /api/auth/change-password/  - Change password
```

### Resource Endpoints

```
GET    /api/products/              - List all products
POST   /api/products/              - Create product
GET    /api/products/{id}/         - Get product details
PUT    /api/products/{id}/         - Update product
DELETE /api/products/{id}/         - Delete product

GET    /api/orders/                - List all orders
POST   /api/orders/                - Create order
GET    /api/orders/{id}/           - Get order details
PUT    /api/orders/{id}/           - Update order
DELETE /api/orders/{id}/           - Delete order

GET    /api/order-items/           - List all order items
POST   /api/order-items/           - Create order item
GET    /api/order-items/{id}/      - Get order item
PUT    /api/order-items/{id}/      - Update order item
DELETE /api/order-items/{id}/      - Delete order item
```

### Authentication Flow

1. **Login**: POST to `/api/auth/login/` with credentials
   - Response: `{ access_token, refresh_token, user }`
2. **API Requests**: Include header `Authorization: Bearer <access_token>`
3. **Token Refresh**: POST to `/api/auth/token/refresh/` with refresh token
4. **Logout**: POST to `/api/auth/logout/` to blacklist tokens

## 🗄️ Database Management

### Connecting with DBeaver

1. Create new connection → PostgreSQL
2. Connection settings:
   - Host: `localhost`
   - Port: `5432`
   - Database: `sales_db`
   - Username: `postgres`
   - Password: `postgres123`
3. Test Connection → Finish

### Docker Database Commands

```bash
# View logs
docker-compose logs -f postgres

# Access PostgreSQL shell
docker exec -it sales_postgres psql -U postgres -d sales_db

# Backup database
docker exec -t sales_postgres pg_dump -U postgres sales_db > backup.sql

# Restore database
docker exec -i sales_postgres psql -U postgres sales_db < backup.sql

# Stop containers
docker-compose down

# Stop and remove volumes (WARNING: deletes all data)
docker-compose down -v
```

## 👨‍💻 Development

### Backend Development

```bash
# Generate model diagram
python3 manage.py graph_models sales -o models.png

# Create new migrations
python3 manage.py makemigrations

# Apply migrations
python3 manage.py migrate

# Create superuser
python3 manage.py createsuperuser
```

### Frontend Development

```bash
# Run dev server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

### Development Guidelines

- Use Ant Design for UI components
- Use React Query for async data management
- Use React Hook Form with Zod for form validation
- Functional components with TypeScript
- Tailwind CSS utility-first styling
- Components should be max 200 lines
- Extract complex logic into custom hooks

## 🔒 Environment Variables

### Backend (.env)

```env
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=sales_db
DB_USER=postgres
DB_PASSWORD=postgres123
DB_HOST=localhost
DB_PORT=5432
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000/api
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ using Django and React**
