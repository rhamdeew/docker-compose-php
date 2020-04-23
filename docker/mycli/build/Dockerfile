FROM python:3.8-alpine
RUN apk add --no-cache --virtual build-essentials \
    gcc libressl-dev musl-dev libffi-dev && \
    pip install mycli && \
    apk del build-essentials && rm -rf /var/cache/apk/*

CMD [ "mycli" ]
