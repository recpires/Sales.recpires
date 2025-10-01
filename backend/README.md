# Sales Backend - Django REST API

A Django backend application for managing sales and shopping items.

## Features

- **Product Management**: Create, read, update, and delete products with SKU, price, and stock tracking
- **Order Management**: Handle customer orders with status tracking (pending, processing, shipped, delivered, cancelled)
- **Order Items**: Link products to orders with quantity and pricing
- **Django Admin Interface**: Fully configured admin panel for easy management
- **REST API**: Django REST Framework integration for API endpoints

## Models

### Product
- Name, description, SKU
- Price and stock tracking
- Active/inactive status
- Timestamps

### Order
- Customer information (name, email, phone, address)
- Order status tracking
- Total amount calculation
- Timestamps

### OrderItem
- Links products to orders
- Quantity and unit price
- Automatic subtotal calculation

## Installation

1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create superuser for admin access:
```bash
python manage.py createsuperuser
```

5. Run development server:
```bash
python manage.py runserver
```

## Usage

- **Admin Interface**: http://localhost:8000/admin/
- **API**: Configure URLs and views as needed

## Project Structure

```
backend/
├── core/           # Main project settings
├── sales/          # Sales app with models, views, admin
├── venv/           # Virtual environment
├── manage.py       # Django management script
└── requirements.txt
```

## Dependencies

- Django 5.2.6
- Django REST Framework 3.16.1
