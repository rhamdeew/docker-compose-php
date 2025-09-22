## Docker Compose PHP

![](https://github.com/rhamdeew/docker-compose-php/workflows/Docker%20Image%20CI/badge.svg)

[RU](README_ru.md)

### Supported PHP versions

- PHP-FPM 8.4.11
- PHP-FPM 8.3.24
- PHP-FPM 8.2.29
- PHP-FPM 8.1.33
- PHP-FPM 8.0.30
- PHP-FPM 7.4.33
- Apache 2 + PHP 8.1.33
- Apache 2 + PHP 7.4.33
- Apache 2 + PHP 5.6.40

To use old versions of PHP you can check [docker-compose-php v. 0.1.9](https://github.com/rhamdeew/docker-compose-php/tree/v0.1.9)

### First local run:

#### Recommended approach: Using manage.py (automated setup)

The project now includes a management script (`manage.py`) that automates the entire setup process:

```
# Initialize default configuration
python manage.py init

# Generate all configurations (docker-compose.yml, nginx configs, project directories, SSL certificates)
python manage.py generate

# Start containers
make up
```

The `manage.py` script will:
- Create `config.yml` with your host configurations
- Generate `docker-compose.yml` with the required PHP versions
- Create Nginx configuration files for each host
- Set up SSL certificates for HTTPS hosts
- Create project directories with test `index.php` files
- Handle all the configuration automatically

#### Optional: Manual setup

If you prefer manual configuration, you can use the traditional approach:

##### 1. Edit your /etc/hosts

```
sudo vim /etc/hosts
```

and add

```
127.0.0.1    site.test
```

##### 2. Copy configs and start containers

```
cp mysql.env.example mysql.env
cp docker/nginx/config/templates/site.test.conf-php-82 docker/nginx/config/site.test.conf
mkdir -p projects/site.test
echo '<?php echo phpversion();' > projects/site.test/index.php
make up
```

<details>
  <summary>Example of using another PHP versions</summary>


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

##### 3. Check started services

http://localhost:8025 - mailpit (super:demo)

http://localhost:8080 - adminer (super:demo)

http://site.test - test site

#### Management script features

The `manage.py` script provides additional functionality for managing your development environment:

```
# View available commands
python manage.py help

# Initialize configuration file
python manage.py init

# Generate/update all configurations
python manage.py generate
```

Key features:
- **Multi-host support**: Configure multiple domains with different PHP versions
- **SSL certificate generation**: Automatic self-signed certificate creation
- **Project directory setup**: Creates directories and test files automatically
- **Apache/Nginx support**: Handles both PHP-FPM and Apache mod_php configurations
- **HTTPS/HTTP support**: Configures both HTTP and HTTPS virtual hosts
- **Aliases and redirects**: Supports domain aliases and www redirects

Configuration is handled through `config.yml`, which defines hosts, PHP versions, SSL settings, and domain aliases.

------

### Management

For ease of management, all basic commands are included in the Makefile. To list the available commands, run cat Makefile.

#### Run:

```
#runs docker-compose up -d
make up
```


#### Stop

```
#runs docker-compose stop
make stop
```


####  View the status of running containers

```
#runs docker-compose ps
make ps
```


#### Viewing container logs

```
#runs docker-compose logs -tail=100 -f (php-82|db|mailpit|nginx)
make logs name=php-82
```

*Database host - db*

### Fine tuning


#### Changing basic auth login/password (super:demo)

Open `docker/nginx/.htpasswd` and replace its contents.


#### Setting files owner ID is the same as on the host

In the terminal, using the id command, we get the digital identifier of our user and group.
Then uncomment the line

```
#RUN usermod -u 1050 www-data && groupmod -g 1050 www-data
```

In `docker/php-82/build/Dockerfile` and replace id 1050 with your identifiers there.
We start containers with a rebuild

```
#runs docker-compose up -d --build
make upb
```


#### php.ini settings

Open `docker/php-82/config/php.ini`
Or edit the php-fpm settings - www.conf


#### Switch PHP version

Uncomment the block with the container of the required php version in docker-compose.yml.

In Nginx config for the site, comment out the old upstream and uncomment the new one.

```
#runs docker-compose stop && docker-compose up -d --build
make st upb
```

In the case of Apache in the Nginx config, you need to comment out the entire block for PHP-FPM and uncomment the one below for Apache.
Also do not forget to tweak Apache configs.


#### Adding a new host

Just copy config `docker/nginx/config/templates/site.test.conf` and tweak it.

In the case of using the container with apache, you must also fix the `docker/apache-php-56/config/sites-enabled/site.test.conf` config.

There are examples of Nginx config files in `docker/nginx/config/disabled/`

#### Connecting to the database from the console

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

#### Connecting to the database from the console

```
#runs docker-compose -f docker-compose.mycli.yml run --rm mycli /bin/ash -c "mycli -uroot -hdb -p\$$MYSQL_ROOT_PASSWORD" || true
make mycli
```

#### Running PHP scripts from the console

```
#runs docker-compose exec $(name) /bin/sh || true
make exec name=php-82
```


#### Route access to the database

The password is registered in the MYSQL_ROOT_PASSWORD parameter in mysql.env


#### Change of database access details

Changed in mysql.env file


#### An example of running Cron background tasks

```
* * * * *    /usr/local/bin/docker-compose -f /srv/www/docker-compose-php/docker-compose.yml exec php-82 /srv/projects/site.test/yii api/send
```

#### Acme.sh

```
#runs docker-compose -f docker-compose.acme.yml run --rm acme acme.sh --issue -d `echo $(d) | sed 's/,/ \-d /g'` -w /acme-challenge
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
#runs docker-compose -f docker-compose.node.yml run --rm node /bin/ash || true
make node
```

#### MySQL Tuner

```
#runs docker-compose -f docker-compose.mysqltuner.yml run --rm mysqltuner /bin/ash -c "/opt/mysqltuner --user root --host db --pass \$$MYSQL_ROOT_PASSWORD --forcemem $(mem)" || true
make mysqltuner mem=4096
```
