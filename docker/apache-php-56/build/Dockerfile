FROM php:5-apache
RUN apt-get update && apt-get -y install libmcrypt-dev libicu-dev wget mysql-client msmtp libpng-dev libjpeg-dev libfreetype6-dev libxpm-dev libvpx-dev && apt-get clean
RUN docker-php-ext-install pdo_mysql
RUN docker-php-ext-install mcrypt
RUN docker-php-ext-install opcache
RUN docker-php-ext-configure gd --with-freetype-dir=/usr/include/ --with-jpeg-dir=/usr/include/ --with-xpm-dir=/usr/include/ --with-vpx-dir=/usr/include/
RUN docker-php-ext-install gd
RUN wget https://github.com/composer/composer/releases/download/1.8.6/composer.phar -O /usr/local/bin/composer && chmod +x /usr/local/bin/composer
RUN docker-php-ext-install mysql
RUN docker-php-ext-install zip
RUN (cd /etc/apache2/mods-enabled && ln -s ../mods-available/rewrite.load .)
#RUN usermod -u 1050 www-data && groupmod -g 1050 www-data
