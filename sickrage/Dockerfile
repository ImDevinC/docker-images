# Run command:
#   docker run -v ${CONFIG_PATH}:/data -v ${MEDIA_PATH}:/media -p 8081:8081 --rm imdevinc/sickrage

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

RUN groupadd -r -g 666 sickrage \
    && useradd -r -u 666 -g 666 -ms /bin/false sickrage \
    && chown sickrage:sickrage /usr/src/sickrage

EXPOSE 8081

ENV SR_VERSION master

USER sickrage
RUN git clone https://github.com/SickRage/SickRage.git /usr/src/sickrage \
    && cd /usr/src/sickrage \
    && git checkout "${SR_VERSION}"

ENTRYPOINT ["python", "SickBeard.py", "--nolaunch"]
CMD ["--datadir", "/data"]


