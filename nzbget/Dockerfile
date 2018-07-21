# Run command:
#   docker run -d --restart always -v ${DOWNLOAD_PATH}:/downloads -v ${CONFIG_PATH}:/nzbget.conf --network plex-net -p 6789:6789 --name nzbget imdevinc/nzbget
# Downloads volume needs to be have read/write access for uid/gid 666

FROM alpine:latest
LABEL maintainer Devin Collins <me@imdevinc.com>
WORKDIR /usr/src/nzbget
EXPOSE 6789
RUN apk add --no-cache \
    curl \
    p7zip \
    python2 \
    unrar \
    wget \
    shadow \
    && rm -rf /var/lib/apt/lists/* && \
    groupadd -r -g 666 nzbget \
    && useradd -r -u 666 -g 666 -ms /bin/false nzbget \
    && chown nzbget:nzbget /usr/src/nzbget

USER nzbget
RUN curl -o /tmp/nzbget.run -L https://nzbget.net/download/nzbget-latest-bin-linux.run \
    && sh /tmp/nzbget.run --destdir /usr/src/nzbget \
    && rm -rf /tmp/*

ENTRYPOINT ["./nzbget", "-s", "-o", "outputmode=log"]
CMD ["-c", "/nzbget.conf"]