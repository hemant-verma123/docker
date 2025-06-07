# Use an official PHP runtime as a parent image
FROM php:7.4-apache

ENV MYSQL_ROOT_USER=root

#PHP Extensions
RUN docker-php-ext-install mysqli

# Set the working directory in the container
WORKDIR /var/www/html

# Enable Apache mod_rewrite
RUN a2enmod rewrite

# Install additional PHP extensions if needed
# RUN docker-php-ext-install ...

# Copy Apache configuration file allowing .htaccess files
COPY ./docker/apache2 /etc/

# Copy all files into the /var/www/html
COPY . /var/www/html

# Expose port 80 for web traffic
EXPOSE 80
