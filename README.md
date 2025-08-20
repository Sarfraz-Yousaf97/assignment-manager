Task Management System
Project Overview
The Task Management System is a Django-based web application that allows users to manage projects and tasks with role-based permissions and JWT authentication. Users can create projects, add tasks, assign roles (Admin, Member, Viewer), and perform CRUD operations based on their permissions. The system includes email verification for user registration and uses Django REST Framework for API development.

Project Name: core
App Name: accounts
Key Features:
User registration and login with JWT authentication
Email verification for new users
Project creation, updating, and deletion
Task management within projects (CRUD operations)
Role-based permissions: Admins manage projects/tasks, Members update task statuses, Viewers have read-only access
Nested API endpoints for projects and tasks



Requirements

Python 3.8+
Django 4.x
Django REST Framework
Django REST Framework Simple JWT
DRF Nested Routers
A database (default: SQLite; configure others like PostgreSQL if needed)
An SMTP server for email verification (optional for production)

Installation
1. Clone the Repository
Clone or download the project to your local machine:
git clone <repository-url>
cd core

2. Set Up a Virtual Environment
Create and activate a virtual environment to isolate dependencies:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install Dependencies
Install the required Python packages:
pip install django djangorestframework djangorestframework-simplejwt drf-nested-routers

4. Configure the Project
The project structure assumes the following:

Project directory: core
App directory: core/accounts
Configuration file: core/core/settings.py

Update core/core/settings.py to include the accounts app and required settings:
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'accounts',  # The app name
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

AUTH_USER_MODEL = 'accounts.User'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # For development

For production email sending, configure an SMTP backend, e.g., for Gmail:
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-specific-password'  # Use an App Password if 2FA is enabled

5. Apply Database Migrations
Set up the database by running migrations:
python manage.py makemigrations
python manage.py migrate

6. Create a Superuser (Optional)
Create a superuser to access the Django admin panel:
python manage.py createsuperuser

7. Run the Development Server
Start the Django server:
python manage.py runserver

The API will be available at http://127.0.0.1:8000/api/.
Project Structure

core/: Django project directory
core/settings.py: Project settings, including app and authentication configurations
core/urls.py: Main URL routing
accounts/: Django app directory
models.py: Custom User, Project, Task, and ProjectRole models
serializers.py: API serializers for data validation and formatting
permissions.py: Custom permission classes for role-based access
views.py: API views for authentication, project, and task management
urls.py: API endpoint routes





API Endpoints
The API uses JWT authentication and supports the following endpoints:
Authentication

Register: POST /api/register/
Body: {"email": "user@example.com", "username": "user", "first_name": "First", "last_name": "Last", "password": "password123"}
Response: {"message": "User created, verification email sent"}


Verify Email: GET /api/verify/<uidb64>/<token>/
Response: {"message": "Email verified successfully"}


Login (Obtain JWT): POST /api/token/
Body: {"email": "user@example.com", "password": "password123"}
Response: {"refresh": "...", "access": "..."}



Project Management

Create Project: POST /api/projects/
Headers: Authorization: Bearer <access_token>
Body: {"title": "New Project", "description": "Description"}


List Projects: GET /api/projects/
Update Project: PUT /api/projects/<id>/
Delete Project: DELETE /api/projects/<id>/
Assign Role: POST /api/projects/<id>/assign_role/
Body: {"user_id": 2, "role": "MEMBER"}


Remove Role: POST /api/projects/<id>/remove_role/
Body: {"user_id": 2}



Task Management

Create Task: POST /api/projects/<project_id>/tasks/
Body: {"title": "New Task", "description": "Task description", "status": "TODO", "assigned_to": 2}


List Tasks: GET /api/projects/<project_id>/tasks/
Update Task: PUT /api/projects/<project_id>/tasks/<task_id>/
Delete Task: DELETE /api/projects/<project_id>/tasks/<task_id>/
Assign Task: POST /api/projects/<project_id>/tasks/<task_id>/assign/
Body: {"user_id": 2}


Unassign Task: POST /api/projects/<project_id>/tasks/<task_id>/unassign/

Permissions

Admins: Can manage projects, tasks, and roles.
Members: Can update task statuses.
Viewers: Have read-only access to projects and tasks.
Authentication: Most endpoints require a JWT token (except /api/register/ and /api/verify/.../).

Testing with cURL
Test the register endpoint:
curl -X POST http://127.0.0.1:8000/api/register/ \
-H "Content-Type: application/json" \
-d '{
  "email": "testuser@example.com",
  "username": "testuser",
  "first_name": "Test",
  "last_name": "User",
  "password": "securepassword123"
}'

Check the console for the verification link, then test verification:
curl -X GET http://127.0.0.1:8000/api/verify/<uidb64>/<token>/

Troubleshooting

ConnectionRefusedError on Register: Ensure EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' in settings.py for development. For production, configure a valid SMTP server.
Authentication Errors: Verify permission_classes = [AllowAny] is set for RegisterView and VerifyEmailView in accounts/views.py.
Database Issues: Run python manage.py migrate to ensure the database schema is up-to-date.
JWT Token: Obtain a token via /api/token/ and include it in headers as Authorization: Bearer <access_token>.

Notes

Email in Production: Replace the console email backend with an SMTP backend and update the verification_link domain in accounts/views.py.
Database: SQLite is used by default. For production, consider PostgreSQL or MySQL.
Security: Ensure HTTPS is enabled in production for secure JWT transmission.

For further details, refer to the Django admin panel (http://127.0.0.1:8000/admin/) or contact the developer.