#!/bin/sh
set -e

# Process templates using environment variables
envsubst '${SERVER_IP}' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf

# Execute the main container command
exec "$@" 