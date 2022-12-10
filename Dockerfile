# syntax=docker/dockerfile:1.2

# BUILDER PORTION
FROM python:3.11.0-slim as build
RUN apt update \
    && apt install -y python3-dev build-essential wget libxml2-dev libproj-dev libsqlite3-dev zlib1g-dev pkg-config git \
    && apt clean
ADD https://github.com/benbjohnson/litestream/releases/download/v0.3.9/litestream-v0.3.9-linux-amd64-static.tar.gz /tmp/litestream.tar.gz
RUN tar -C /usr/local/bin -xzf /tmp/litestream.tar.gz

# enables latest sqlite (JSON1 + FTS5 extensions); see https://www.sqlite.org/download.html
RUN wget "https://www.sqlite.org/2022/sqlite-autoconf-3400000.tar.gz" && tar xzf sqlite-autoconf-3400000.tar.gz \
    && cd sqlite-autoconf-3400000 && ./configure --disable-static --enable-fts5 --enable-json1 CFLAGS="-g -O2 -DSQLITE_ENABLE_FTS3=1 -DSQLITE_ENABLE_FTS4=1 -DSQLITE_ENABLE_RTREE=1 -DSQLITE_ENABLE_JSON1" \
    && make && make install

# install requirements, after upgrading pip
COPY app/requirements.txt requirements.txt
RUN pip3 install -U pip && pip3 install -r requirements.txt

# TARGET PORTION
FROM python:3.11.0-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY --from=build /usr/local/lib/ /usr/local/lib/
COPY --from=build /usr/local/bin /usr/local/bin
COPY --from=build /usr/local/bin/litestream /usr/local/bin/litestream
ENV LD_LIBRARY_PATH=/usr/local/lib

# variables are used in litestream.yml and run.sh
ARG RUNFILE=/scripts/run.sh
ENV DB_FILE=/db/x.db
ENV METADATA_PATH=/db/metadata.yml
ENV REPLICA_URL=s3://corpus-x/db
ENV DS_PORT=8080

# opens up port for use, note `DS_PORT`
EXPOSE $DS_PORT

# copy Datasette metadata + Litestream configuration file & startup script, enable access with chmod 777
COPY app/db/metadata.yml $METADATA_PATH
COPY app/etc/litestream.yml /etc/litestream.yml
COPY app/scripts/run.sh $RUNFILE
RUN chmod 777 $RUNFILE

# entry script
CMD [ "/scripts/run.sh" ]