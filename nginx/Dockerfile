FROM nginx:1.25

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy templates
COPY conf.d/local.conf.template /etc/nginx/templates/default.conf.template
COPY conf.d/prod.conf.template /etc/nginx/conf.d/prod.conf.template

# Create directory for SSL certificates
RUN mkdir -p /etc/nginx/ssl/live/localhost

# Use envsubst via entrypoint script
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]

CMD ["nginx", "-g", "daemon off;"] 