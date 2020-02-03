FROM php:7.1-fpm-alpine
RUN apk add --no-cache mysql-client msmtp perl wget procps

ENV LD_PRELOAD /usr/lib/preloadable_libiconv.so php
RUN apk add --no-cache --repository http://dl-3.alpinelinux.org/alpine/edge/community gnu-libiconv && \
    apk add --no-cache --virtual build-essentials \
    icu-dev icu-libs zlib-dev g++ make automake autoconf shadow libzip-dev \
    libpng-dev libwebp-dev libjpeg-turbo-dev freetype-dev && \
    docker-php-ext-configure gd \
    --with-gd \
    --with-freetype-dir=/usr/include/ \
    --with-png-dir=/usr/include/ \
    --with-jpeg-dir=/usr/include/ && \
    docker-php-ext-install gd && \
    docker-php-ext-install mysqli && \
    docker-php-ext-install pdo_mysql && \
    docker-php-ext-install intl && \
    docker-php-ext-install opcache && \
    docker-php-ext-install exif && \
    docker-php-ext-install zip && \
    apk del build-essentials && rm -rf /usr/src/php*

RUN wget https://github.com/composer/composer/releases/download/1.9.2/composer.phar -O /usr/local/bin/composer && chmod +x /usr/local/bin/composer

RUN wget http://mysqltuner.pl/ -O /opt/mysqltuner && \
    wget https://raw.githubusercontent.com/major/MySQLTuner-perl/master/basic_passwords.txt -O /opt/basic_passwords.txt && \
    wget https://raw.githubusercontent.com/major/MySQLTuner-perl/master/vulnerabilities.csv -O /opt/vulnerabilities.csv && \
    chmod +x /opt/mysqltuner

#RUN usermod -u 1050 www-data && groupmod -g 1050 www-data