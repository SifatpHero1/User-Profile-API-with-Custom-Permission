# User Profile API with Custom Permission

A Django REST Framework (DRF) based User Profile Management API with custom permission control, JWT authentication, and integrated Product management.

## Features

- ✅ User Registration & Authentication (JWT)
- ✅ User Profile Management (CRUD)
- ✅ Custom Permission Control - Only owners can modify their own data
- ✅ Product Management with owner-based access control
- ✅ Automatic Profile Creation via Django signals
- ✅ Media File Upload support for avatars and product images
- ✅ Pagination Support (2 items per page)
- ✅ API Root Endpoint at `/`

## Tech Stack

- **Backend**: Django 5.2.12
- **API Framework**: Django REST Framework (DRF)
- **Authentication**: Simple JWT
- **Database**: SQLite (development)
- **Python**: 3.13

## Project Structure

```
drf_custom_permission_project/
├── config/                  # Project settings
│   ├── settings.py          # Django settings
│   ├── urls.py              # Root URL configuration
│   └── wsgi.py              # WSGI application
├── accounts/                # User management app
│   ├── models.py            # UserProfile model
│   ├── serializers.py       # API serializers
│   ├── permissions.py       # Custom permissions
│   ├── views.py             # API views
│   ├── urls.py              # URL routes
│   ├── signals.py           # Auto-profile creation
│   └── apps.py              # App config
├── products/                # Product management app
│   ├── models.py            # Product model
│   ├── serializers.py       # API serializers
│   ├── permissions.py       # Custom permissions
│   ├── views.py             # API views
│   ├── urls.py              # URL routes
│   └── apps.py              # App config
└── manage.py                # Django management script
```

## Installation

```bash
# Navigate to the Django project
cd drf_custom_permission_project

# Install dependencies
pip install djangorestframework djangorestframework-simplejwt django-cors-headers Pillow

# Run database migrations
python manage.py makemigrations
python manage.py migrate

# Create a superuser (optional)
python manage.py createsuperuser

# Run the development server
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

## API Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/api/register/` | Register new user | Public |
| POST | `/api/login/` | Login & get JWT tokens | Public |
| POST | `/api/logout/` | Logout (blacklist refresh token) | Authenticated |
| GET | `/api/profile/` | Get current user profile | Authenticated |
| PATCH | `/api/profile/update/` | Update user profile | Authenticated (Owner only) |
| GET | `/api/products/` | List all products | Public |
| POST | `/api/products/` | Create a product | Authenticated |
| GET | `/api/products/{id}/` | Get product details | Public |
| PUT/PATCH | `/api/products/{id}/` | Update product | Authenticated (Owner only) |
| DELETE | `/api/products/{id}/` | Delete product | Authenticated (Owner only) |

## Postman Testing Guide (8 Steps)

### Step 1: Register User 1 (Sifat)

**Method:** `POST`  
**URL:** `http://127.0.0.1:8000/api/register/`  
**Body (JSON):**
```json
{
  "username": "sifat101",
  "email": "sifat101@gmail.com",
  "first_name": "Sifat",
  "last_name": "User",
  "password": "12345678",
  "password2": "12345678"
}
```

**Expected:** `201 Created`  
**Action:** Copy the `access` token → Save as `sifat101_token`

---

### Step 2: Login User 1

**Method:** `POST`  
**URL:** `http://127.0.0.1:8000/api/login/`  
**Body (JSON):**
```json
{
  "username": "sifat101",
  "password": "12345678"
}
```

**Expected:** `200 OK` with tokens  
**Action:** Save `access` token as `sifat101_token`

---

### Step 3: Create Product as Sifat101

**Method:** `POST`  
**URL:** `http://127.0.0.1:8000/api/products/`  
**Headers:**
```
Authorization: Bearer sifat101_token
Content-Type: application/json
```
**Body (JSON):**
```json
{
  "name": "Sifat Test Product",
  "description": "Created by sifat101",
  "price": "100.00",
  "stock": 5
}
```

**Expected:** `201 Created`  
**Note:** `owner` is auto-assigned. Remember `product_id` (e.g., `1`)

---

### Step 4: Register User 2

**Method:** `POST`  
**URL:** `http://127.0.0.1:8000/api/register/`  
**Body (JSON):**
```json
{
  "username": "sifat102",
  "email": "sifat102@gmail.com",
  "first_name": "Sifat",
  "last_name": "Second",
  "password": "12345678",
  "password2": "12345678"
}
```

**Expected:** `201 Created`

---

### Step 5: Login User 2

**Method:** `POST`  
**URL:** `http://127.0.0.1:8000/api/login/`  
**Body (JSON):**
```json
{
  "username": "sifat102",
  "password": "12345678"
}
```

**Expected:** `200 OK`  
**Action:** Save `access` token as `sifat102_token`

---

### Step 6: Permission Test (User 2 → User 1's Product)

**Method:** `PATCH`  
**URL:** `http://127.0.0.1:8000/api/products/1/`  
**Headers:**
```
Authorization: Bearer sifat102_token
Content-Type: application/json
```
**Body (JSON):**
```json
{
  "price": "999.00"
}
```

**Expected:** `403 Forbidden`  
**Explanation:** Only product owner (sifat101) can modify

---

### Step 7: Owner Update Test (User 1 → Own Product)

**Method:** `PATCH`  
**URL:** `http://127.0.0.1:8000/api/products/1/`  
**Headers:**
```
Authorization: Bearer sifat101_token
Content-Type: application/json
```
**Body (JSON):**
```json
{
  "price": "150.00",
  "stock": 10
}
```

**Expected:** `200 OK` with updated product

---

### Step 8: Pagination Test

**Settings:** `PAGE_SIZE = 2` (2 products per page)

**Method:** `GET`  
**URL:** `http://127.0.0.1:8000/api/products/?page=1`  
**Headers:**
```
Authorization: Bearer sifat101_token
```

**Expected:** `200 OK`
```json
{
  "count": 3,
  "next": "http://127.0.0.1:8000/api/products/?page=2",
  "previous": null,
  "results": [/* 2 products */]
}
```

**Next Page:** `http://127.0.0.1:8000/api/products/?page=2`

---

## Custom Permission System

### Account-Level Permission (`accounts/permissions.py`)

```python
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        owner = getattr(obj, 'user', obj)
        return owner == request.user
```

### Product-Level Permission (`products/permissions.py`)

```python
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user
```

---

## JWT Configuration

```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}
```

---

## Signals

Auto-create `UserProfile` when a new user registers:

```python
@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
```

---

## Models

### UserProfile

```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Product

```python
class Product(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
```

---

## License

MIT License
