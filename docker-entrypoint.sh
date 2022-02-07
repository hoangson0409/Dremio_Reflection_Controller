#!/bin/bash

set -e
if [ -f ".env_secret" ]; then
  crudini --merge .env < .env_secret
fi
dockerize -wait-retry-interval 3s -timeout 60s -wait tcp://${DB_HOST}:${DB_PORT}

cd /bicon/
if [[ ( ! -z ${AUTO_MIGRATION+x} ) && ( "true" == "${AUTO_MIGRATION}" ) ]]; then
    echo "Executing migrations ..."
    python manage.py migrate
fi

exec "$@"
