FROM nginx:alpine
RUN apk --no-cache add openssl
RUN openssl dhparam -dsaparam -out /etc/nginx/dhparam.pem 4096
