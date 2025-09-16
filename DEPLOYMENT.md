# Render Deployment Guide for Matrichaya Properties

## Prerequisites
1. GitHub repository with your code
2. Render account (free tier available)

## Deployment Steps

### Method 1: Using render.yaml (Recommended)
1. Push your code to GitHub
2. Connect your GitHub repository to Render
3. Render will automatically detect the `render.yaml` file
4. The deployment will be configured automatically

### Method 2: Manual Configuration
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure the following settings:
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command**: `gunicorn matrichaya_properties.wsgi:application`
   - **Environment**: Python 3

### Environment Variables
Set these in Render dashboard:
- `DEBUG`: `False`
- `SECRET_KEY`: Generate a new secret key
- `ALLOWED_HOSTS`: `your-app-name.onrender.com`

### Database Setup
1. Create a PostgreSQL database service on Render
2. The `DATABASE_URL` will be automatically provided
3. Run migrations: `python manage.py migrate`

### Static Files
- Static files are automatically collected during build
- WhiteNoise middleware handles static file serving
- Media files are stored locally (consider using cloud storage for production)

## Local Development
1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and configure
3. Run migrations: `python manage.py migrate`
4. Start development server: `python manage.py runserver`

## Notes
- The app uses SQLite for local development and PostgreSQL for production
- Static files are served by WhiteNoise in production
- Security settings are automatically applied in production mode
