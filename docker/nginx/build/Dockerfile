FROM nginx:alpine
RUN apk --no-cache add openssl
RUN openssl dhparam -dsaparam -out /etc/nginx/dhparam.pem 4096
RUN mkdir /etc/nginx/default_ssl/ && openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout /etc/nginx/default_ssl/nginx.key -out /etc/nginx/default_ssl/nginx.crt -subj "/C=PE/ST=Lima/L=Lima/O=Acme Inc. /OU=IT Department/CN=acme.com"
