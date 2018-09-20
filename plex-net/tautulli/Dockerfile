FROM alpine:latest
LABEL maintainer Devin Collins <me@imdevinc.com>
WORKDIR /usr/src/tautulli
EXPOSE 8181
RUN apk add --no-cache \
    git \
    python \
    shadow \
    py-setuptools \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -ms /bin/false tautulli \
    && chown tautulli:tautulli /usr/src/tautulli \
    && mkdir /data \
    && chown tautulli:tautulli /data
VOLUME /data
USER tautulli
RUN git clone https://github.com/Tautulli/Tautulli.git .

ENTRYPOINT ["python", "Tautulli.py", "--nolaunch"]
CMD ["--config", "/data/config.ini", "--datadir", "/data"]
