## Nginx + MariaDB + MailHog + PHP-71/72/73/74 FPM + Apache mod-php 56/71

![](https://github.com/rhamdeew/docker-compose-php/workflows/Docker%20Image%20CI/badge.svg)

[Readme на русском](README_ru.md)

### Management

For ease of management, all basic commands are included in the Makefile. To list the available commands, run cat Makefile.


#### First run:

```
cp mysql.env.example mysql.env
#edit mysql.env
make up
```

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
#docker-compose logs -tail=100 -f (php-74|db|mailhog|nginx)
make logs name=php-74
```


#### After launch, services are available at:

http://localhost:8025 - mailhog (demo:demo)

http://localhost:8080 - adminer (demo:demo)

http://site.test - тестовый сайт (необходимо прописать этот хост в hosts)

*В настройках подключения к БД нужно прописать хост db*


### Fine tuning


#### Change login/password super: demo

Open docker/nginx/.htpasswd and replace its contents.


#### Host user permissions

In the terminal, using the id command, we get the digital identifier of our user and group.
Then uncomment the line

```
#RUN usermod -u 1050 www-data && groupmod -g 1050 www-data
```

In docker /*php*/build/Dockerfile and replace 1050 with your identifiers there.
We start containers with a rebuild

```
#docker-compose up -d --build
make upb
```


#### php.ini settings

Open docker/php-74/config/php.ini
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

Just copy config docker/nginx/config/site.test.conf and tweak it.

In the case of using the container with apache, you must also fix the docker/apache-php-56/config/sites-enabled/site.test.conf config.

There are examples of Nginx config files in docker/nginx/config/disabled/


#### Connect to the database from the console

```
#docker-compose exec php-74 /bin/ash и затем mysql --host=db -u<юзер> -p<пароль>
make mysql
```


#### Run php scripts from the console

```
#docker-compose exec php-74 /bin/ash
make php
```


#### Route access to the database

The password is registered in the MYSQL_ROOT_PASSWORD parameter in mysql.env


#### Change of database access details

Changed in mysql.env file


#### An example of running Cron background tasks

```
* * * * *    /usr/local/bin/docker-compose -f /srv/www/docker-compose-php/docker-compose.yml exec php-74 /srv/projects/site.test/yii api/send
```

#### Acme.sh

```
#docker-compose run --rm acme acme.sh --issue -d site.ru -w /acme-challenge
make ssl d="site.ru,www.site.ru"
```
SSL certificates are saved in the docker/nginx/ssl directory. To make it work you need to uncomment
lines in the docker-compose.yml config

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
02 3 * * * /usr/local/bin/docker-compose -f /srv/www/docker-compose-php/docker-compose.yml exec nginx nginx -t && /usr/local/bin/docker-compose -f /srv/www/docker-compose-php/docker-compose.yml restart nginx
```

If you need to run acme.sh for some other purpose, you can do this with this command:

```
make acme
```

#### Node.js

```
#docker-compose run --rm node-10 /bin/ash
make node
```

#### MySQL Tuner

```
#docker-compose exec php-74 /bin/ash -c "/opt/mysqltuner --user root --host db --pass superpass --forcemem 4096"
make mysqltuner mem=4096
```
