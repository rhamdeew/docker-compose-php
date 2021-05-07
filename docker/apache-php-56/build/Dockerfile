FROM php:5.6-apache
RUN apt-get update && \
    apt-get -y install libmcrypt4 libvpx4 libfreetype6 libjpeg62-turbo libpng16-16 libxpm4 wget mysql-client msmtp && \
    apt-get -y install libmcrypt-dev libicu-dev libpng-dev libjpeg-dev libfreetype6-dev libxpm-dev libvpx-dev && \
    docker-php-ext-install pdo_mysql && \
    docker-php-ext-install mcrypt && \
    docker-php-ext-install opcache && \
    docker-php-ext-configure gd --with-freetype-dir=/usr/include/ --with-jpeg-dir=/usr/include/ --with-xpm-dir=/usr/include/ --with-vpx-dir=/usr/include/ && \
    docker-php-ext-install gd && \
    docker-php-ext-install mysql && \
    docker-php-ext-install zip && \
    apt-get remove -y libmcrypt-dev libicu-dev libpng-dev libjpeg-dev libfreetype6-dev libxpm-dev libvpx-dev gcc gcc-6 && \
    apt-get autoremove -y && apt-get clean && rm -rf /usr/src/* && rm -rf /var/lib/apt/lists/*

RUN (cd /etc/apache2/mods-enabled && ln -s ../mods-available/rewrite.load .)
RUN wget https://getcomposer.org/composer-stable.phar -O /usr/local/bin/composer && chmod +x /usr/local/bin/composer
#RUN usermod -u 1050 www-data && groupmod -g 1050 www-data
