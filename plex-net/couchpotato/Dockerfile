# Adapted from https://hub.docker.com/r/couchpotato/couchpotato/~/dockerfile/
# Run command:
#   docker run -d --restart always -v ${DATA_PATH}:/data -v ${MOVIE_PATH}:/movies -v ${DOWNLOAD_PATH}:/downloads --network plex-net -p 5050:5050 --name couchpotato imdevinc/couchpotato
# Make sure that the /data, /movies and /downloads volumes are readable/writeable by UID/GID 666

FROM alpine:latest
LABEL maintainer Devin Collins <me@imdevinc.com>
WORKDIR /usr/src/couchpotato

RUN apk add --no-cache \
        ca-certificates \
        gcc \
        git \
        libffi-dev \
        libxml2-dev \
        libxslt-dev \
        musl-dev \
        openssl-dev \
        python \
        python-dev \
        py2-pip \
        shadow \
        && rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/false couchpotato \
    && chown couchpotato: /usr/src/couchpotato \
    && mkdir /data \
    && chown couchpotato: /data

RUN pip install \
        lxml \
        pyopenssl

EXPOSE 5050
VOLUME /data
USER couchpotato
RUN git clone https://github.com/CouchPotato/CouchPotatoServer.git /usr/src/couchpotato \
    && cd /usr/src/couchpotato

ENTRYPOINT ["python", "CouchPotato.py"]
CMD ["--data_dir", "/data", "--console_log"]
