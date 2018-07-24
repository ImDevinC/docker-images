FROM alpine:latest
LABEL maintainer Devin Collins <me@imdevinc.com>
WORKDIR /usr/src/tautulli
EXPOSE 8181
RUN apk add --no-cache \
    git \
    python \
    shadow \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -u 605 -ms /bin/false tautulli \
    && chown tautulli:tautulli /usr/src/tautulli

USER tautulli
RUN git clone https://github.com/Tautulli/Tautulli.git .

ENTRYPOINT ["python", "Tautulli.py", "--nolaunch"]
CMD ["--config", "/data/config.ini", "--datadir", "/data"]