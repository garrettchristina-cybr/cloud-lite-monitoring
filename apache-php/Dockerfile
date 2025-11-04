FROM php:8.2-apache

# Install PHP extensions for MySQL
RUN docker-php-ext-install mysqli pdo pdo_mysql

# Enable useful Apache modules
RUN a2enmod rewrite

WORKDIR /var/www/html

# Ensure Apache log dir exists and is writable
RUN mkdir -p /var/log/apache2 && chown -R www-data:www-data /var/log/apache2