# Run command:
#   docker run -d --restart always -v ${CONFIG_PATH}:/data -v ${DOWNLOAD_PATH}:/downloads -v ${ANIME_PATH}:/anime -v ${TV_PATH}:/tv\ shows --network plex-net -p 8081:8081 --name sickrage  imdevinc/sickrage
# Downloads volume needs to be have read/write access for uid/gid 666

FROM alpine:latest
LABEL maintainer Devin Collins <me@imdevinc.com>
WORKDIR /usr/src/sickrage

RUN apk add --no-cache \
    git \
    python \
    shadow \
    unrar \
    openssl \
    openssl-dev \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/false sickrage \
    && chown sickrage: /usr/src/sickrage \
    && mkdir /data \
    && chown sickrage: /data

EXPOSE 8081
VOLUME /data

USER sickrage
WORKDIR /usr/src/sickrage
RUN git clone https://github.com/pymedusa/Medusa.git /usr/src/sickrage \
    && git checkout $(git tag | tail -n1) \
    && git pull

ENTRYPOINT ["python", "SickBeard.py", "--nolaunch"]
CMD ["--datadir", "/data"]
