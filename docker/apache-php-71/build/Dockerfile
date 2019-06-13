FROM php:7.1-apache
RUN apt-get update && apt-get -y install libmcrypt-dev libicu-dev libpng-dev libjpeg-dev libfreetype6-dev libxpm-dev wget mysql-client && apt-get clean
RUN docker-php-ext-install pdo_mysql
RUN docker-php-ext-install mcrypt
RUN docker-php-ext-install opcache
RUN docker-php-ext-configure gd --with-freetype-dir=/usr/include/ --with-jpeg-dir=/usr/include/ --with-xpm-dir=/usr/include/
RUN docker-php-ext-install gd
RUN wget https://github.com/composer/composer/releases/download/1.8.6/composer.phar -O /usr/local/bin/composer && chmod +x /usr/local/bin/composer
RUN docker-php-ext-install mysqli
RUN docker-php-ext-install zip
RUN (cd /etc/apache2/mods-enabled && ln -s ../mods-available/rewrite.load .)
RUN apt-get update && apt-get -y install msmtp && apt-get clean
#RUN usermod -u 1050 www-data && groupmod -g 1050 www-data
