# Deployment Guide

## Initial Setup

1. Clone the repository:
```bash
git clone <your-repository-url>
cd image-sharing-app
```

2. Create and configure environment files:
```bash
cp .env.example .env.prod
# Edit .env.prod with your settings
```

### Environment Variables

Important environment variables for deployment:

- `DEBUG`: Set to 'False' for production
- `SECRET_KEY`: Set a secure secret key
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts (include your server IP)
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`: Database credentials
- `SERVER_IP`: Your server's public IP address

3. Set the SERVER_IP environment variable for your deployment:
```bash
export SERVER_IP=your-server-ip
```

## Deployment

1. Build and start the containers:
```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

2. Create a superuser (optional):
```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

3. Access the application:
- Main site: http://your-server-ip
- Admin interface: http://your-server-ip/admin

## Updating the Application

When pulling updates from git:

```bash
# Pull the latest changes
git pull

# Rebuild and restart containers
export SERVER_IP=your-server-ip
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up --build -d
```

## Common Issues

1. **DEBUG mode enabled**: Make sure DEBUG=False in your .env.prod file
2. **Cannot access site**: Check if your server IP is added to ALLOWED_HOSTS
3. **Database connection errors**: Verify database credentials and connectivity 