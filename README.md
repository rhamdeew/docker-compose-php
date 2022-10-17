## Nginx + MariaDB + MailHog + PHP-7.4/8.0/8.1 FPM + Apache mod-php 5.6/7.4/8.1

![](https://github.com/rhamdeew/docker-compose-php/workflows/Docker%20Image%20CI/badge.svg)

[Russian Readme](README_ru.md)

### First local run:

All you have to do is run these commands:

##### 1. Edit your /etc/hosts

```
sudo vim /etc/hosts
```

and add

```
127.0.0.1    site.test
```

##### 2. Run these commands

```
cp mysql.env.example mysql.env
cp docker/nginx/config/templates/site.test.conf-php-81 docker/nginx/config/site.test.conf
mkdir -p projects/site.test
echo '<?php echo phpversion();' > projects/site.test/index.php
make up
```

<details>
  <summary>Another options</summary>


  ```
cp mysql.env.example mysql.env
#edit mysql.env

#you can choose the template with specific php version
cp templates/docker-compose-php-81.yml docker-compose.yml


#and copy specific config for Nginx + PHP-FPM
cp docker/nginx/config/templates/site.test.conf-php-81 docker/nginx/config/site.test.conf

#or copy configs for Nginx + Apache PHP
cp templates/docker-compose-apache-php-74.yml docker-compose.yml
cp docker/nginx/config/templates/site.test.conf-apache-php-74 docker/nginx/config/site.test.conf
cp docker/apache-php-74/config/templates/site.test.conf docker/apache-php-74/config/sites-enabled/site.test.conf


mkdir -p projects/site.test
echo '<?php echo phpversion();' > projects/site.test/index.php

make up
  ```

</details>

##### 3. Test running services

http://localhost:8025 - mailhog (super:demo)

http://localhost:8080 - adminer (super:demo)

http://site.test - test site

------

### Management

For ease of management, all basic commands are included in the Makefile. To list the available commands, run cat Makefile.

#### Run:

```
#docker-compose up -d
make up
```


#### Stop

```
#docker-compose stop
make stop
```


####  View the status of running containers

```
#docker-compose ps
make ps
```


#### Viewing container logs

```
#docker-compose logs -tail=100 -f (php-81|db|mailhog|nginx)
make logs name=php-81
```

*Database host - db*

### Fine tuning


#### Change login/password super:demo

Open `docker/nginx/.htpasswd` and replace its contents.


#### Host user permissions

In the terminal, using the id command, we get the digital identifier of our user and group.
Then uncomment the line

```
#RUN usermod -u 1050 www-data && groupmod -g 1050 www-data
```

In `docker/php-81/build/Dockerfile` and replace id 1050 with your identifiers there.
We start containers with a rebuild

```
#docker-compose up -d --build
make upb
```


#### php.ini settings

Open `docker/php-81/config/php.ini`
Or edit the php-fpm settings - www.conf


#### Switch php version

Uncomment the block with the container of the required php version in docker-compose.yml.

In Nginx config for the site, comment out the old upstream and uncomment the new one.

```
#docker-compose stop && docker-compose up -d --build
make st upb
```

In the case of Apache in the Nginx config, you need to comment out the entire block for PHP-FPM and uncomment the one below for Apache.
Also do not forget to tweak Apache configs.


#### Adding a new host

Just copy config `docker/nginx/config/templates/site.test.conf` and tweak it.

In the case of using the container with apache, you must also fix the `docker/apache-php-56/config/sites-enabled/site.test.conf` config.

There are examples of Nginx config files in `docker/nginx/config/disabled/`

#### Connect to the database from the console

```
make php
mysql -uroot -hdb -pMYSQL_ROOT_PASSWORD
```

Example with importing SQL-dump:

```
make php
mysql -uroot -hdb -pMYSQL_ROOT_PASSWORD
> create database test;

mysql -uroot -hdb -pMYSQL_ROOT_PASSWORD test < dump.sql
```

#### Connect to the database from the console

```
#docker-compose -f docker-compose.mycli.yml run --rm mycli /bin/ash -c "mycli -uroot -hdb -p\$$MYSQL_ROOT_PASSWORD" || true
make mycli
```

#### Run php scripts from the console

```
#docker-compose exec $(name) /bin/sh || true
make exec name=php-81
```


#### Route access to the database

The password is registered in the MYSQL_ROOT_PASSWORD parameter in mysql.env


#### Change of database access details

Changed in mysql.env file


#### An example of running Cron background tasks

```
* * * * *    /usr/local/bin/docker-compose -f /srv/www/docker-compose-php/docker-compose.yml exec php-81 /srv/projects/site.test/yii api/send
```

#### Acme.sh

```
#docker-compose -f docker-compose.acme.yml run --rm acme acme.sh --issue -d `echo $(d) | sed 's/,/ \-d /g'` -w /acme-challenge
make ssl d="site.ru,www.site.ru"
```

SSL certificates are saved in the `docker/nginx/ssl directory`. To make it work you need to uncomment
lines in the `docker-compose.yml` config

```
      # - ./docker/nginx/ssl:/etc/nginx/ssl:ro
```

Also uncomment the line

```
      # -"443:443"
```

*crontab*

```
00 3 * * * /usr/local/bin/docker-compose -f /srv/www/docker-compose-php/docker-compose.acme.yml run --rm acme acme.sh --cron
02 3 * * * /usr/local/bin/docker-compose -f /srv/www/docker-compose-php/docker-compose.yml exec -T nginx nginx -t -q && /usr/local/bin/docker-compose -f /srv/www/docker-compose-php/docker-compose.yml restart nginx
```

If you need to run `acme.sh` for some other purpose, you can do this with this command:

```
make acme
```

#### Node.js

```
#docker-compose -f docker-compose.node.yml run --rm node-10 /bin/ash || true
make node
```

#### MySQL Tuner

```
#docker-compose -f docker-compose.mysqltuner.yml run --rm mysqltuner /bin/ash -c "/opt/mysqltuner --user root --host db --pass \$$MYSQL_ROOT_PASSWORD --forcemem $(mem)" || true
make mysqltuner mem=4096
```
