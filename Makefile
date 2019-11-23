up:
	docker-compose up -d
upb:
	docker-compose up -d --build
stop:
	docker-compose stop
st: stop
ps:
	docker-compose ps

#make logs name=php-73
logs:
	docker-compose logs --tail=100 -f $(name) || true
nlogs:
	docker-compose logs --tail=100 -f nginx || true
plogs:
	docker-compose logs --tail=100 -f php-73 || true
dblogs:
	docker-compose logs --tail=100 -f db || true
dbpass:
	cat docker-compose.yml | grep MYSQL_ROOT_PASSWORD:
mysql:
	docker-compose exec php-73 mysql -uroot -hdb -p || true

#make rs name=php-73
rs:
	docker-compose restart $(name)
nrs:
	docker-compose restart nginx

#make exec name=php-73
exec:
	docker-compose exec $(name) /bin/sh || true
ex: exec

php:
	docker-compose exec php-73 /bin/ash || true
pex: php
	
#make acme d="site.ru,www.site.ru"
acme:
	docker-compose -f docker-compose.acme.yml run --rm acme acme.sh --issue -d `echo $(d) | sed 's/,/ \-d /g'` -w /acme-challenge
ssl: acme

node:
	docker-compose -f docker-compose.node.yml run --rm node /bin/bash || true
