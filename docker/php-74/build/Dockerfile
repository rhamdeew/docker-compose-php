FROM php:7.3-fpm-alpine
RUN apk add --no-cache icu-dev icu-libs icu msmtp git vim mysql-client zlib zlib-dev \
ssmtp g++ make automake bash libpng-dev autoconf shadow libzip-dev
RUN apk add --no-cache freetype libpng libjpeg-turbo freetype-dev libpng-dev libjpeg-turbo-dev && \
  docker-php-ext-configure gd \
    --with-gd \
    --with-freetype-dir=/usr/include/ \
    --with-png-dir=/usr/include/ \
    --with-jpeg-dir=/usr/include/ && \
  NPROC=$(grep -c ^processor /proc/cpuinfo 2>/dev/null || 1) && \
  docker-php-ext-install -j${NPROC} gd && \
  apk del --no-cache freetype-dev libpng-dev libjpeg-turbo-dev
RUN docker-php-ext-install mysqli
RUN docker-php-ext-install pdo_mysql
RUN docker-php-ext-install intl
RUN docker-php-ext-install opcache
RUN docker-php-ext-install exif
RUN docker-php-ext-install zip
RUN wget https://github.com/composer/composer/releases/download/1.9.2/composer.phar -O /usr/local/bin/composer && chmod +x /usr/local/bin/composer
ENV LD_PRELOAD /usr/lib/preloadable_libiconv.so php
RUN apk add --no-cache --repository http://dl-3.alpinelinux.org/alpine/edge/community gnu-libiconv
RUN docker-php-ext-install iconv
#RUN usermod -u 1050 www-data && groupmod -g 1050 www-data
