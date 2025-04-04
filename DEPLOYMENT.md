# Deployment Guide

## Prerequisites

Before proceeding with the deployment, ensure that Docker and Git are installed on your system:

### Installing Git
```bash
# For Ubuntu/Debian
sudo apt update
sudo apt install git -y

# For CentOS/RHEL/Amazon Linux 2023
sudo yum install git -y

# Verify installation
git --version
```

### Installing Docker and Docker Compose
```bash
# Install Docker on Ubuntu/Debian
sudo apt update
sudo apt install apt-transport-https ca-certificates curl software-properties-common -y
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt update
sudo apt install docker-ce -y

# Install Docker on CentOS/RHEL/Amazon Linux 2023
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install docker-ce docker-ce-cli containerd.io -y

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.18.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installations
docker --version
docker-compose --version

# Add your user to the docker group (optional, to run docker without sudo)
sudo usermod -aG docker $USER
# Note: You'll need to log out and back in for this change to take effect
```

## Initial Setup

1. Clone the repository:
```bash
git clone <your-repository-url>
cd image-sharing-app
```

2. Create and configure environment files:
```bash
cp .env.prod.example .env.prod
# Edit .env.prod with your settings
```

### Environment Variables

Important environment variables for deployment:

- `DEBUG`: Set to 'False' for production
- `SECRET_KEY`: Set a secure secret key (use a random string generator, e.g., `python -c "import secrets; print(secrets.token_urlsafe(50))"`)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts (include your server IP)
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`: Database credentials
- `SERVER_IP`: Your server's public IP address
- `USE_SSL`: Set to 'true' to enable HTTPS (requires SSL certificates)
- `DOMAIN_NAME`: Your domain name (used for SSL configuration)

## Deployment

1. Build and start the containers:
```bash
docker-compose -f docker-compose.prod.yml --env-file .env.prod up --build -d
```

2. Run database migrations:
```bash
docker-compose -f docker-compose.prod.yml --env-file .env.prod exec web python manage.py migrate
```

3. Create a superuser (optional):
```bash
docker-compose -f docker-compose.prod.yml --env-file .env.prod exec web python manage.py createsuperuser
```

4. Access the application:
- Main site: http://your-server-ip
- Admin interface: http://your-server-ip/admin

## Updating the Application

When pulling updates from git:

```bash
# Pull the latest changes
git pull

# Rebuild and restart containers
docker-compose -f docker-compose.prod.yml --env-file .env.prod down
docker-compose -f docker-compose.prod.yml --env-file .env.prod up --build -d
```

## SSL Configuration

The application can run with or without SSL. By default, it runs over HTTP. To enable HTTPS:

1. Set `USE_SSL=true` in your `.env.prod` file
2. Set `DOMAIN_NAME=your-domain.com` in your `.env.prod` file
3. Mount your SSL certificates by uncommenting this line in docker-compose.prod.yml:
   ```yaml
   # - ./ssl:/etc/nginx/ssl
   ```
4. Ensure your SSL certificates are in the `./ssl` directory with the following structure:
   ```
   ssl/
   └── live/
       └── your-domain.com/
           ├── fullchain.pem
           └── privkey.pem
   ```
5. Deploy your application as usual:
   ```bash
   docker-compose -f docker-compose.prod.yml --env-file .env.prod up --build -d
   ```

If you don't have SSL certificates, keep `USE_SSL=false` and the application will run over HTTP.

## Storage Configuration

The application can use either local storage or AWS S3 for storing media files. This flexibility allows you to start with local storage and migrate to S3 later when needed.

### Deploying Without S3 (Default)

By default, the application uses local file storage. To ensure this configuration:

1. Set `USE_S3=False` in your `.env.prod` file (or omit this variable entirely)
```
# Local storage settings
USE_S3=False
```

2. Deploy your application as usual:
```bash
docker-compose -f docker-compose.prod.yml --env-file .env.prod up --build -d
```

With this configuration, all media files will be stored in the Docker volume.

### Migrating to AWS S3

To switch to S3 storage after your application is already running:

1. Create an S3 bucket:
   - Log in to AWS console and go to S3
   - Create a new bucket with a unique name
   - Uncheck "Block all public access" (as media files need to be publicly readable)
   - In bucket permissions, add a bucket policy for public read access:
   ```json
   {
      "Version": "2012-10-17",
      "Statement": [
         {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::your-bucket-name/*"
         }
      ]
   }
   ```

2. Create IAM user with S3 access:
   - Go to IAM service and create a new user
   - Attach the "AmazonS3FullAccess" policy (or a more limited policy for production)
   - Save the Access Key ID and Secret Access Key

3. Update your `.env.prod` file with S3 credentials:
   ```
   # AWS S3 settings
   USE_S3=True
   AWS_ACCESS_KEY_ID=your-access-key-id
   AWS_SECRET_ACCESS_KEY=your-secret-access-key
   AWS_STORAGE_BUCKET_NAME=your-bucket-name
   AWS_S3_REGION_NAME=your-region (e.g., eu-west-1)
   ```

4. Restart your application:
   ```bash
   docker-compose -f docker-compose.prod.yml --env-file .env.prod down
   docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
   ```

5. Migrate existing media files (optional):
   - If you have existing media files in local storage, you'll need to manually upload them to your S3 bucket
   - Use the AWS CLI or the S3 console to copy files from your server to the appropriate S3 locations

After these changes, new file uploads will go directly to S3 instead of local storage.

## Common Issues

1. **DEBUG mode enabled**: Make sure DEBUG=False in your .env.prod file
2. **Cannot access site**: Check if your server IP is added to ALLOWED_HOSTS
3. **Database connection errors**: Verify database credentials and connectivity
4. **S3 storage issues**: Verify AWS credentials and bucket permissions 