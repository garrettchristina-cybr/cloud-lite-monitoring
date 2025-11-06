FROM php:8.2-apache

# system deps for extensions (curl is usually present, but this ensures headers)
RUN apt-get update && apt-get install -y libcurl4-openssl-dev && rm -rf /var/lib/apt/lists/*

# PHP extensions
RUN docker-php-ext-install mysqli pdo pdo_mysql
RUN docker-php-ext-install curl || true  # no-op if already enabled

RUN a2enmod rewrite

WORKDIR /var/www/html
RUN mkdir -p /var/log/apache2 && chown -R www-data:www-data /var/log/apache2