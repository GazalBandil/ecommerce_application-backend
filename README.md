﻿
# E-commerce Backend System Using FastAPI

## Introduction

### Objective

This project is a RESTful backend API built using **FastAPI** for an e-commerce platform. It provides robust and secure functionality for:

* Admin product management (CRUD)
* User authentication and password recovery
* Product listing, filtering, and detail views
* Shopping cart management and dummy checkout
* Order history and tracking

### Scope

The scope of this project includes only backend development. No frontend UI is implemented. The API can be tested and reviewed using tools such as **Postman**.

### Prerequisites

* Python 3.10+
* Postman
* Basic knowledge of RESTful APIs and HTTP methods

---

## Technology Stack

* **Backend Framework**: FastAPI
* **ORM**: SQLAlchemy
* **Database**: PostgreSQL
* **Authentication**: JWT (access and refresh tokens)
* **Schema Validation**: Pydantic
* **Logging**: Python's built-in logging module

---

## Features

* Secure JWT-based authentication system with role-based access control (RBAC)
* Admin-only product CRUD APIs
* Public product listing and detail APIs with filters and search
* Shopping cart functionality
* Dummy payment and order checkout system
* Order history and order details
* Password recovery via secure email token
* Input validation, structured logging, and consistent error handling

---

## API Endpoints

### Authentication & User Management

* `POST /auth/signup` - User registration
* `POST /auth/signin` - User login (returns JWT tokens)
* `POST /auth/forgot-password` - Sends password reset email
* `POST /auth/reset-password` - Resets password using secure token

### Admin Product Management (Admin Only)

* `POST /admin/products` - Create product
* `GET /admin/products` - List all products (paginated)
* `GET /admin/products/{id}` - Get product by ID
* `PUT /admin/products/{id}` - Update product
* `DELETE /admin/products/{id}` - Delete product

### Public Product APIs

* `GET /products` - Public product listing with filters
* `GET /products/search` - Keyword-based product search
* `GET /products/{id}` - View product details

### Cart Management (User Only)

* `POST /cart` - Add product to cart
* `GET /cart` - View cart items
* `DELETE /cart/{product_id}` - Remove product from cart
* `PUT /cart/{product_id}` - Update product quantity in cart

### Checkout (User Only)

* `POST /checkout` - Dummy payment and place order

### Orders (User Only)

* `GET /orders` - View order history
* `GET /orders/{order_id}` - View specific order details

---

## Project Structure

```
C:.
|   main.py
|   __init__.py
|
+---auth
|   |   dependencies.py
|   |   email.py
|   |   models.py
|   |   routes.py
|   |   schemas.py
|   |   utils.py
|   |
|   \---__pycache__
|           dependencies.cpython-311.pyc
|           email.cpython-311.pyc
|           models.cpython-311.pyc
|           routes.cpython-311.pyc
|           schemas.cpython-311.pyc
|           utils.cpython-311.pyc
|
+---cart
|   |   models.py
|   |   routes.py
|   |   schemas.py
|   |
|   \---__pycache__
|           models.cpython-311.pyc
|           routes.cpython-311.pyc
|           schemas.cpython-311.pyc
|
+---core
|   |   database.py
|   |   deps.py
|   |   error_logger.py
|   |   logging.py
|   |
|   \---__pycache__
|           database.cpython-311.pyc
|           deps.cpython-311.pyc
|           error_logger.cpython-311.pyc
|           logging.cpython-311.pyc
|
+---middlewares
|   |   access_logger.py
|   |
|   \---__pycache__
|           access_logger.cpython-311.pyc
|
+---orders
|   |   checkout_routes.py
|   |   models.py
|   |   orders_routes.py
|   |   schemas.py
|   |
|   \---__pycache__
|           checkout_routes.cpython-311.pyc
|           models.cpython-311.pyc
|           orders_routes.cpython-311.pyc
|           routes.cpython-311.pyc
|           schemas.cpython-311.pyc
|
+---products
|   |   models.py
|   |   public_routes.py
|   |   routes.py
|   |   schemas.py
|   |
|   \---__pycache__
|           models.cpython-311.pyc
|           public_routes.cpython-311.pyc
|           routes.cpython-311.pyc
|           schemas.cpython-311.pyc
|
+---tests
+---utils
\---__pycache__
        main.cpython-311.pyc
        __init__.cpython-311.pyc
```
---

# # Setup Instructions

1. **Clone the Repository**

   ```bash
   git clone https://github.com/GazalBandil/ecommerce_application-backend.git
   cd fastapi-ecommerce-backend
   ```

2. **Create Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   Create a `.env` file in the root:

   ```
   DATABASE_URL=postgresql://user:password@localhost/dbname
   JWT_SECRET_KEY=your-secret-key
   EMAIL_USER=your-email
   EMAIL_PASSWORD=your-app-password
   ```

6. **Start the Server**

   ```bash
   uvicorn app.main:app --reload
   ```

7. **Access API Docs**
   Open Swagger UI at: `http://localhost:8000/docs`

---

## Error Handling Format

All API responses follow a consistent error format:

```json
{
  "error": true,
  "message": "Description of the error",
  "code": 400
}
```

---

## Logging

* Logs API requests, authentication attempts, and errors.
* Logging module is placed under `app/middlewares/logging.py`.
* Logs include timestamps, status codes, endpoints, and IPs.

---

