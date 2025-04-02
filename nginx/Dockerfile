FROM nginx:1.25

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Install gettext for envsubst
RUN apt-get update && apt-get install -y gettext-base && rm -rf /var/lib/apt/lists/*

# Copy config templates
COPY conf.d/local.conf.template /etc/nginx/templates/
COPY conf.d/prod.conf /etc/nginx/conf.d/

# Create directory for SSL certificates
RUN mkdir -p /etc/nginx/ssl/live/your-domain.com

# Set default configuration based on environment
ENV NGINX_ENV=local
ENV SERVER_IP=localhost

# Use envsubst to replace environment variables in template
CMD ["sh", "-c", "envsubst < /etc/nginx/templates/local.conf.template > /etc/nginx/conf.d/local.conf && cp /etc/nginx/conf.d/${NGINX_ENV}.conf /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"] 