#!/bin/sh
set -e

# Default to local environment
if [ -z "$ENVIRONMENT" ]; then
    ENVIRONMENT="local"
fi

# Default USE_SSL to false if not set
if [ -z "$USE_SSL" ]; then
    USE_SSL="false"
fi

if [ "$ENVIRONMENT" = "production" ]; then
    # HTTP configuration (used when SSL is disabled)
    HTTP_CONFIG=$(cat << EOF
    location / {
        proxy_pass http://django;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Host \$host;
        proxy_redirect off;
        proxy_connect_timeout 300s;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }

    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    location /media/ {
        alias /app/media/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
EOF
)

    # Check if SSL is enabled and certificates exist
    if [ "$USE_SSL" = "true" ] && [ -f /etc/nginx/ssl/live/${DOMAIN_NAME:-localhost}/fullchain.pem ] && [ -f /etc/nginx/ssl/live/${DOMAIN_NAME:-localhost}/privkey.pem ]; then
        echo "Using production configuration with SSL"
        # Set variables for template
        export SSL_REDIRECT="return 301 https://\$host\$request_uri;"
        export HTTP_CONFIG=""
        export SSL_SERVER=$(cat << EOF
server {
    listen 443 ssl;
    server_name ${SERVER_IP};
    client_max_body_size 100M;

    ssl_certificate /etc/nginx/ssl/live/${DOMAIN_NAME:-localhost}/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/live/${DOMAIN_NAME:-localhost}/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://django;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Host \$host;
        proxy_redirect off;
    }

    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    location /media/ {
        alias /app/media/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
}
EOF
)
    else
        echo "Using production HTTP configuration without SSL"
        # Set variables for HTTP-only template
        export SSL_REDIRECT=""
        export HTTP_CONFIG="$HTTP_CONFIG"
        export SSL_SERVER=""
    fi

    # Process the production template
    envsubst '${SERVER_IP} ${SSL_REDIRECT} ${HTTP_CONFIG} ${SSL_SERVER}' < /etc/nginx/conf.d/prod.conf.template > /etc/nginx/conf.d/default.conf
else
    # Use local template for development
    envsubst '${SERVER_IP}' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf
    echo "Using local development configuration"
fi

# Execute the main container command
exec "$@" 