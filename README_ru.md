## Nginx + MariaDB + MailHog + PHP-71/72/73/74 FPM + Apache mod-php 56/71

![](https://github.com/rhamdeew/docker-compose-php/workflows/Docker%20Image%20CI/badge.svg)

### Управление

Для удобства управления все основные команды внесены в Makefile. Для просмотра доступных команд выполните cat Makefile.


#### Первый запуск:

```
cp mysql.env.example mysql.env
#edit mysql.env
make up
```

#### Запуск:

```
#docker-compose up -d
make up
```


#### Остановка

```
#docker-compose stop
make stop
```


#### Просмотр статуса запущеных контейнеров

```
#docker-compose ps
make ps
```


#### Просмотр логов контейнера

```
#docker-compose logs -tail=100 -f (php-74|db|mailhog|nginx)
make logs name=php-74
```


#### После запуска сервисы доступны по адресам:

http://localhost:8025 - mailhog (demo:demo)

http://localhost:8080 - adminer (demo:demo)

http://site.test - тестовый сайт (необходимо прописать этот хост в hosts)

*В настройках подключения к БД нужно прописать хост db*


### Тонкая настройка


#### Смена логина/пароля super:demo

Открываем docker/nginx/.htpasswd и заменяем его содержимое


#### Права на файлы как у хостового юзера

В терминале командой id получаем цифровой идентификатор своего юзера и группы.
Затем раскомменчиваем строчку

```
#RUN usermod -u 1050 www-data && groupmod -g 1050 www-data
```

В docker/*php*/build/Dockerfile и заменяем там 1050 на свои идентификаторы.
Запускаем все с ребилдом

```
#docker-compose up -d --build
make upb
```


#### Настройки php.ini

Открываем docker/php-74/config/php.ini
Или же редактируем настройки php-fpm - www.conf


#### Переключение версии php

Раскомменчиваем в docker-compose.yml блок с контейнером необходимой версии php.

В конфиге Nginx для сайта закомменчиваем старый апстрим и раскомменчиваем новый.

```
#docker-compose stop && docker-compose up -d --build
make st upb
```

В случае с Apache в конфиге Nginx необходимо закомментировать весь блок для PHP-FPM и раскомментировать тот что ниже для Apache.
Также не забыть подправить конфиги Apache.


#### Добавление нового хоста

Достаточно скопировать конфиг docker/nginx/config/site.test.conf и немного его подправить.

В случае с использованием контейнера с apache необходимо также поправить конфиг docker/apache-php-56/config/sites-enabled/site.test.conf

Есть примеры конфигов для Nginx в docker/nginx/config/disabled/


#### Подключиться к БД с консоли

```
#docker-compose exec php-74 /bin/ash и затем mysql --host=db -u<юзер> -p<пароль>
make mysql
```


#### Запускать php-скрипты из консоли

```
#docker-compose exec php-74 /bin/ash
make php
```


#### Рутовый доступ к БД

Пароль прописан в параметре MYSQL_ROOT_PASSWORD в mysql.env


#### Смена реквизитов доступа к БД

Меняется в файле mysql.env


#### Пример запуска фоновых задач по Cron

```
* * * * *    /usr/local/bin/docker-compose -f /srv/www/docker-compose-php/docker-compose.yml exec php-74 /srv/projects/site.test/yii api/send
```

#### Acme.sh

```
#docker-compose run --rm acme acme.sh --issue -d site.ru -w /acme-challenge
make ssl d="site.ru,www.site.ru"
```

SSL-сертификаты сохраняются в директорию docker/nginx/ssl. Чтобы все заработало нужно раскомментировать
строчки в конфиге docker-compose.yml

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
02 3 * * * /usr/local/bin/docker-compose -f /srv/www/docker-compose-php/docker-compose.yml exec nginx nginx -t && /usr/local/bin/docker-compose -f /srv/www/docker-compose-php/docker-compose.yml restart nginx
```

Если нужно запустить acme.sh для каких-то других целей это можно сделать данной командой:

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
