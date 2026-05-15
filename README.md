# SmartBook — Smart Appointment Booking System

A full-stack web application built with Django, MySQL, and Bootstrap 5.

## Tech Stack

- **Backend**: Django 6, Django REST Framework
- **Database**: MySQL
- **Frontend**: Bootstrap 5, HTML/CSS/JavaScript
- **Auth**: Django built-in auth with custom User model

## Roles

| Role | Access |
|------|--------|
| Admin | Full platform management, analytics |
| Provider | Manage schedule, accept/reject appointments |
| User | Browse providers, book appointments, leave reviews |

## Setup

### 1. Clone and create virtual environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Copy `.env.example` to `.env` and fill in your values:

```bash
copy .env.example .env
```

### 4. Create MySQL database

```sql
CREATE DATABASE appointment_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Seed demo data

```bash
python seed_data.py
```

### 7. Run the server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000

## Demo Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | Admin@1234 |
| Provider | dr_sarah | Provider@1234 |
| User | john_doe | User@1234 |

## Project Structure

```
appointment-system/
├── config/              # Django project settings & URLs
├── accounts/            # Custom user model, auth views
├── appointments/        # Booking logic, conflict detection
├── providers/           # Provider profiles, availability slots
├── notifications/       # In-app notification system
├── reviews/             # Ratings and reviews
├── dashboard/           # Role-based dashboards, landing page
├── templates/           # All HTML templates
├── static/              # CSS, JS, images
├── media/               # User-uploaded files
├── seed_data.py         # Demo data seeder
└── requirements.txt
```

## Key Features

- Role-based access control (Admin / Provider / User)
- Double-booking conflict prevention
- Real-time notification badge (polling)
- Star rating system with interactive UI
- Provider search with category and rating filters
- Responsive Bootstrap 5 UI with dark navbar
- Toast notifications for all actions
- Django admin panel fully configured
