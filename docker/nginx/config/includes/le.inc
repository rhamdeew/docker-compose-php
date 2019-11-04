    location ^~ /.well-known/acme-challenge {
        allow all;
        root /usr/share/nginx/html;
    }