FROM alpine:latest
RUN apk add --update python py-pip bash
RUN apk add --no-cache -X http://dl-cdn.alpinelinux.org/alpine/edge/main py-psycopg2

ADD . /usr/src/app
COPY ./requirements /usr/requirements/

WORKDIR /usr/requirements/

RUN pip install -r production.txt

RUN adduser -D user
WORKDIR /usr/src/app

RUN chown -R user.user .

USER user

CMD bash bin/run.sh
