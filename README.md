# Django Image Sharing App

A modern image sharing application built with Django, featuring user authentication, image uploads, and a responsive design.

## Features

- User authentication (login, register, logout)
- Image upload and management
- User profiles
- Image likes and comments
- Responsive design with Bootstrap
- Search functionality
- AWS S3 integration for media storage (in production)

## Prerequisites

- Docker
- Docker Compose
- Python 3.11+ (for local development)

## Project Structure

```
image-sharing-app/
├── image_sharing_app/     # Main Django app
├── templates/             # HTML templates
├── static/                # Static files
├── media/                 # User uploaded files (not version controlled)
├── nginx/                 # Nginx configuration
├── config/                # Django project settings
├── docker-compose.local.yml  # Local development setup
├── docker-compose.prod.yml   # Production setup
└── requirements.txt       # Python dependencies
```

## Getting Started

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd image-sharing-app
```

2. Create and configure environment files:
```bash
cp .env.example .env.local
# Edit .env.local with your settings
```

3. Build and start the containers:
```bash
docker-compose -f docker-compose.local.yml up --build
```

4. Create a superuser (optional):
```bash
docker-compose -f docker-compose.local.yml exec web python manage.py createsuperuser
```

5. Access the application:
- Main site: http://127.0.0.1:8000
- Admin interface: http://127.0.0.1:8000/admin

### Production Deployment

For detailed production deployment instructions, please see the [Deployment Guide](DEPLOYMENT.md).

## Development Commands

```bash
# Start containers
docker-compose -f docker-compose.local.yml up

# Stop containers
docker-compose -f docker-compose.local.yml down

# Stop containers and remove volumes
docker-compose -f docker-compose.local.yml down -v

# View logs
docker-compose -f docker-compose.local.yml logs -f

# Create superuser
docker-compose -f docker-compose.local.yml exec web python manage.py createsuperuser

# Run migrations
docker-compose -f docker-compose.local.yml exec web python manage.py migrate

# Collect static files
docker-compose -f docker-compose.local.yml exec web python manage.py collectstatic
```

## Data Persistence

The application uses Docker volumes for data persistence:
- `image-sharing-app_media`: Stores user-uploaded images and files
- `image-sharing-app_static`: Stores collected static files
- `image-sharing-app_postgres_data`: Stores the PostgreSQL database data

Important notes:
- Volume data is not pushed to GitHub
- Each developer needs to set up their own volumes locally
- In production, use proper backup strategies for volume data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Django
- Bootstrap
- PostgreSQL
- Nginx
- Docker
