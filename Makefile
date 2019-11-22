up:
	docker-compose up -d
upb:
	docker-compose up -d --build
stop:
	docker-compose stop
st:
	docker-compose stop
ps:
	docker-compose ps

#make logs name=php-73
logs:
	docker-compose logs --tail=100 -f $(name)
nlogs:
	docker-compose logs --tail=100 -f nginx
dblogs:
	docker-compose logs --tail=100 -f db

#make rs name=php-73
rs:
	docker-compose restart $(name)
nrs:
	docker-compose restart nginx

#make exec name=php-73
exec:
	docker-compose exec $(name) /bin/sh

#make ex name=php-73
ex:
	docker-compose exec $(name) /bin/sh
pex:
	docker-compose exec php-73 /bin/ash
	
#make acme d="site.ru,www.site.ru"
acme:
	docker-compose -f docker-compose.acme.yml run --rm acme acme.sh --issue -d `echo $(d) | sed 's/,/ \-d /g'` -w /acme-challenge
