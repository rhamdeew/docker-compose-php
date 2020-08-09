FROM alpine:3.12
RUN apk add --no-cache mysql-client perl perl-doc wget procps

RUN wget http://mysqltuner.pl/ -O /opt/mysqltuner && \
    wget https://raw.githubusercontent.com/major/MySQLTuner-perl/master/basic_passwords.txt -O /opt/basic_passwords.txt && \
    wget https://raw.githubusercontent.com/major/MySQLTuner-perl/master/vulnerabilities.csv -O /opt/vulnerabilities.csv && \
    chmod +x /opt/mysqltuner

CMD ["/opt/mysqltuner"]
