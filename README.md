# Django Image Sharing App

A modern image sharing application built with Django, featuring user authentication, image uploads, and a responsive design.

## Features

- User authentication (login, register, logout)
- Image upload and management
- User profiles
- Image likes and interactions
- Responsive design with Bootstrap
- Search functionality
- AWS S3 integration for media storage (in production)

## Prerequisites

- Docker
- Docker Compose
- Python 3.11+ (for local development)

## Project Structure

```
django-imagesharing-app/
├── images/                 # Main Django app
├── templates/             # HTML templates
├── static/               # Static files
├── media/                # User uploaded files (not version controlled)
├── nginx/                # Nginx configuration
├── docker-compose.local.yml  # Local development setup
├── docker-compose.prod.yml   # Production setup
├── .env.local           # Local environment variables
├── .env.prod            # Production environment variables
└── requirements.txt     # Python dependencies
```

## Data Persistence

The application uses Docker volumes for data persistence:
- `django-imagesharing-app_media`: Stores user-uploaded images and files
- `django-imagesharing-app_static`: Stores collected static files
- `django-imagesharing-app_db`: Stores the PostgreSQL database data

Important notes:
- Volume data is not pushed to GitHub
- Each developer needs to set up their own volumes locally
- In production, use proper backup strategies for volume data
- For development, you can use `docker-compose down -v` to reset all data

## Getting Started

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd django-imagesharing-app
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

1. Configure production environment:
```bash
cp .env.example .env.prod
# Edit .env.prod with your production settings
```

2. Build and start the containers:
```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

## Environment Variables

### Local Development (.env.local)
```
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=127.0.0.1

# Database settings
DB_NAME=imagesharing_local
DB_USER=imagesharing_user
DB_PASSWORD=your-password
DB_HOST=db
DB_PORT=5432

# Local storage settings
USE_S3=False
```

### Production (.env.prod)
```
DEBUG=False
SECRET_KEY=your-secure-secret-key
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database settings
DB_NAME=imagesharing
DB_USER=imagesharing_user
DB_PASSWORD=your-secure-password
DB_HOST=db
DB_PORT=5432

# AWS S3 settings
USE_S3=True
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=your-region
```

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

# Volume Management
docker volume rm django-imagesharing-app_media    # Remove media volume
docker volume rm django-imagesharing-app_static  # Remove static volume
docker volume prune                              # Remove all unused volumes
docker volume prune -f                           # Remove all volumes (including used ones)
```

## Production Deployment

1. Set up AWS resources:
   - Create an S3 bucket for media storage
   - Configure IAM user with S3 access
   - Set up SSL certificates

2. Configure domain and DNS settings

3. Deploy the application:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

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
- AWS S3
