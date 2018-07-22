# Run command:
#   docker run -d --restart always -v ${CONFIG_PATH}:/data -v ${DOWNLOAD_PATH}:/downloads -v ${MEDIA_PATH}:/media --network plex-net -p 8081:8081 imdevinc/sickrage
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

RUN groupadd -r -g 600 media \
    && groupadd -r -g 602 sickrage \
    && useradd -r -u 602 -g sickrage -G media -ms /bin/false sickrage \
    && chown sickrage:sickrage /usr/src/sickrage

EXPOSE 8081

ENV SR_VERSION master

USER sickrage
RUN git clone https://github.com/SickRage/SickRage.git /usr/src/sickrage \
    && cd /usr/src/sickrage \
    && git checkout "${SR_VERSION}"

ENTRYPOINT ["python", "SickBeard.py", "--nolaunch"]
CMD ["--datadir", "/data"]


