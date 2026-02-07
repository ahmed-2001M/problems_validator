#!/bin/bash
set -e

# Ensure MySQL data directory exists and has correct permissions
mkdir -p /var/lib/mysql
chown -R mysql:mysql /var/lib/mysql
mkdir -p /run/mysqld
chown -R mysql:mysql /run/mysqld

# Ensure MySQL data directory is initialized
if [ ! -d "/var/lib/mysql/mysql" ]; then
    echo "Initializing MySQL database..."
    mysqld --initialize-insecure --user=mysql --datadir=/var/lib/mysql
fi

# Start MySQL temporarily to setup users and database
mysqld_safe --user=mysql --datadir=/var/lib/mysql &
MYSQL_PID=$!

# Wait for MySQL to be ready
until mysqladmin ping >/dev/null 2>&1; do
  echo "Waiting for MySQL..."
  sleep 2
done

# Create database and user if they don't exist
# We use environment variables or defaults from docker-compose
DB_NAME=${MYSQL_DATABASE:-problems_validator}
DB_USER=${MYSQL_USER:-user}
DB_PASS=${MYSQL_PASSWORD:-123}

mysql -e "CREATE DATABASE IF NOT EXISTS \`$DB_NAME\`;"
mysql -e "CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';"
mysql -e "GRANT ALL PRIVILEGES ON \`$DB_NAME\`.* TO '$DB_USER'@'localhost';"
mysql -e "FLUSH PRIVILEGES;"

# Run migrations
python manage.py migrate --noinput

# Create admin user if requested (optional)
if [ "$CREATE_SUPERUSER" = "True" ]; then
    python create_admin.py || echo "Superuser creation failed or already exists"
fi

# Stop the temporary MySQL process
kill $MYSQL_PID
wait $MYSQL_PID

# Start Supervisor to manage both MySQL and Gunicorn
exec /usr/bin/supervisord -c /app/supervisord.conf
