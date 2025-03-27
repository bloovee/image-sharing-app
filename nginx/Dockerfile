FROM nginx:1.25

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy local nginx config
COPY conf.d/local.conf /etc/nginx/conf.d/local.conf

# Create directory for SSL certificates
RUN mkdir -p /etc/nginx/ssl/live/your-domain.com

# Set default configuration based on environment
ENV NGINX_ENV=local
CMD ["sh", "-c", "cp /etc/nginx/conf.d/${NGINX_ENV}.conf /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"] 