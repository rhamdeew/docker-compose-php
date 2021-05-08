FROM python:3.9-alpine
RUN apk add --no-cache --virtual build-essentials \
    gcc libressl-dev musl-dev libffi-dev cargo && \
    pip install --no-cache-dir mycli && \
    apk del build-essentials && rm -rf /var/cache/apk/* /root/.cache/* /root/.cargo/* 

CMD [ "mycli" ]
