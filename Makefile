up:
	docker-compose up -d --remove-orphans
upb:
	docker-compose up -d --build --remove-orphans
stop:
	docker-compose stop
st: stop
ps:
	docker-compose ps

#make logs name=php-74
logs:
	docker-compose logs --tail=100 -f $(name) || true
nlogs:
	docker-compose logs --tail=100 -f nginx || true
plogs:
	docker-compose logs --tail=100 -f php-74 || true
dblogs:
	docker-compose logs --tail=100 -f db || true
mysql:
	docker-compose exec php-74 /bin/ash -c "mysql -uroot -hdb -p\$$MYSQL_ROOT_PASSWORD" || true
#make mysqltuner mem=4096
mysqltuner:
	docker-compose exec php-74 /bin/ash -c "/opt/mysqltuner --user root --host db --pass \$$MYSQL_ROOT_PASSWORD --forcemem $(mem)" || true


#make rs name=php-74
rs:
	docker-compose restart $(name)
nrs:
	docker-compose restart nginx

#make exec name=php-74
exec:
	docker-compose exec $(name) /bin/sh || true
ex: exec

php:
	docker-compose exec php-74 /bin/ash || true
pex: php

#make ssl d="site.ru,www.site.ru"
ssl:
	docker-compose -f docker-compose.acme.yml run --rm acme acme.sh --issue -d `echo $(d) | sed 's/,/ \-d /g'` -w /acme-challenge

acme:
	docker-compose -f docker-compose.acme.yml run --rm acme acme.sh

node:
	docker-compose -f docker-compose.node.yml run --rm node-10 /bin/ash || true

mycli:
	docker-compose -f docker-compose.mycli.yml run --rm mycli /bin/ash -c "mycli -uroot -hdb -p\$$MYSQL_ROOT_PASSWORD" || true
