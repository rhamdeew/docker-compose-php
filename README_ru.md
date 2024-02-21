## Nginx + MariaDB + MailHog + PHP-7.4/8.0/8.1/8.2 FPM + Apache mod-php 5.6/7.4/8.1 + Nodejs 20

![](https://github.com/rhamdeew/docker-compose-php/workflows/Docker%20Image%20CI/badge.svg)


### Поддерживаемые версии PHP

- PHP-FPM 8.2.16
- PHP-FPM 8.1.27
- PHP-FPM 8.0.30
- PHP-FPM 7.4.33
- Apache 2 + PHP 8.1.27
- Apache 2 + PHP 7.4.33
- Apache 2 + PHP 5.6.40

Для использования предыдущих версий PHP вы можете взять релиз [docker-compose-php v. 0.1.9](https://github.com/rhamdeew/docker-compose-php/tree/v0.1.9)


### Скринкаст на YouTube

Разворачиваем Wordpress

[![](http://img.youtube.com/vi/_1DKwP7YuTY/0.jpg)](http://www.youtube.com/watch?v=_1DKwP7YuTY "")


#### Первый запуск:

##### 1. Отредактируйте /etc/hosts

```
sudo vim /etc/hosts
```

и добавьте

```
127.0.0.1    site.test
```

##### 2. Скопируйте конфиги и запустите контейнеры

```
cp mysql.env.example mysql.env
cp docker/nginx/config/templates/site.test.conf-php-82 docker/nginx/config/site.test.conf
mkdir -p projects/site.test
echo '<?php echo phpversion();' > projects/site.test/index.php
make up
```

<details>
  <summary>Примеры использования других версий PHP</summary>

  ```
cp mysql.env.example mysql.env
#edit mysql.env

#вы можете выбрать версию PHP
cp templates/docker-compose-php-81.yml docker-compose.yml

  
#и скопировать соответствующий конфиг для Nginx + PHP-FPM
cp docker/nginx/config/templates/site.test.conf-php-81 docker/nginx/config/site.test.conf

#или скопировать соответствующие конфиги для варианта Nginx + Apache PHP
cp templates/docker-compose-apache-php-74.yml docker-compose.yml
cp docker/nginx/config/templates/site.test.conf-apache-php-74 docker/nginx/config/site.test.conf
cp docker/apache-php-74/config/templates/site.test.conf docker/apache-php-74/config/sites-enabled/site.test.conf

  
mkdir -p projects/site.test
echo '<?php echo phpversion();' > projects/site.test/index.php

make up
  ```
</details>

##### 3. Протестируйте запущенные сервисы

http://localhost:8025 - mailhog (super:demo)

http://localhost:8080 - adminer (super:demo)

http://site.test - тестовый сайт

*В настройках подключения к БД нужно прописать хост db*

------

### Управление

Для удобства управления все основные команды внесены в Makefile. Для просмотра доступных команд выполните cat Makefile.

#### Запуск:

```
#вызывает docker-compose up -d
make up
```


#### Остановка

```
#вызывает docker-compose stop
make stop
```


#### Просмотр статуса запущеных контейнеров

```
#вызывает docker-compose ps
make ps
```


#### Просмотр логов контейнера

```
#вызывает docker-compose logs -tail=100 -f (php-82|db|mailhog|nginx)
make logs name=php-82
```


### Тонкая настройка


#### Смена логина/пароля super:demo

Открываем `docker/nginx/.htpasswd` и заменяем его содержимое


#### Права на файлы как у хостового юзера

В терминале командой id получаем цифровой идентификатор своего юзера и группы.
Затем раскомменчиваем строчку

```
#RUN usermod -u 1050 www-data && groupmod -g 1050 www-data
```

В `docker/php-82/build/Dockerfile` и заменяем там 1050 на свои идентификаторы.
Запускаем все с ребилдом

```
#вызывает docker-compose up -d --build
make upb
```


#### Настройки php.ini

Открываем `docker/php-82/config/php.ini`
Или же редактируем настройки php-fpm - www.conf


#### Переключение версии php

Раскомменчиваем в `docker-compose.yml` блок с контейнером необходимой версии php.

В конфиге Nginx для сайта закомменчиваем старый апстрим и раскомменчиваем новый.

```
#вызывает docker-compose stop && docker-compose up -d --build
make st upb
```

В случае с Apache в конфиге Nginx необходимо закомментировать весь блок для PHP-FPM и раскомментировать тот что ниже для Apache.
Также не забыть подправить конфиги Apache.


#### Добавление нового хоста

Достаточно скопировать шаблон конфига `docker/nginx/config/templates/site.test.conf` и немного его подправить.

В случае с использованием контейнера с apache необходимо также поправить конфиг `docker/apache-php-56/config/sites-enabled/site.test.conf`

Есть примеры конфигов для Nginx в `docker/nginx/config/disabled/`


#### Подключиться к БД с консоли

```
#вызывает docker-compose -f docker-compose.mycli.yml run --rm mycli /bin/ash -c "mycli -uroot -hdb -p\$$MYSQL_ROOT_PASSWORD" || true
make mycli
```


#### Запускать php-скрипты из консоли

```
#вызывает docker-compose exec $(name) /bin/sh || true
make exec name=php-82
```


#### Рутовый доступ к БД

Пароль прописан в параметре MYSQL_ROOT_PASSWORD в mysql.env


#### Смена реквизитов доступа к БД

Меняется в файле mysql.env


#### Пример запуска фоновых задач по Cron

```
* * * * *    /usr/local/bin/docker-compose -f /srv/www/docker-compose-php/docker-compose.yml exec php-82 /srv/projects/site.test/yii api/send
```

#### Acme.sh

```
#docker-compose -f docker-compose.acme.yml run --rm acme acme.sh --issue -d `echo $(d) | sed 's/,/ \-d /g'` -w /acme-challenge
make ssl d="site.ru,www.site.ru"
```

SSL-сертификаты сохраняются в директорию `docker/nginx/ssl`. Чтобы все заработало нужно раскомментировать
строчки в конфиге `docker-compose.yml`

```
      # - ./docker/nginx/ssl:/etc/nginx/ssl:ro
```

А также раскомментировать строчку

```
      # -"443:443"
```

*crontab*

```
00 3 * * * /usr/local/bin/docker-compose -f /srv/www/docker-compose-php/docker-compose.acme.yml run --rm acme acme.sh --cron
02 3 * * * /usr/local/bin/docker-compose -f /srv/www/docker-compose-php/docker-compose.yml exec -T nginx nginx -t -q && /usr/local/bin/docker-compose -f /srv/www/docker-compose-php/docker-compose.yml restart nginx
```

Если нужно запустить `acme.sh` для каких-то других целей это можно сделать данной командой:

```
make acme
```

#### Node.js

```
#docker-compose -f docker-compose.node.yml run --rm node /bin/ash || true
make node
```

#### MySQL Tuner

```
#docker-compose -f docker-compose.mysqltuner.yml run --rm mysqltuner /bin/ash -c "/opt/mysqltuner --user root --host db --pass \$$MYSQL_ROOT_PASSWORD --forcemem $(mem)" || true
make mysqltuner mem=4096
```
