# Adapted from https://hub.docker.com/r/couchpotato/couchpotato/~/dockerfile/
# Run command:
#   docker run -d --restart always -v $(pwd):/data -v ${MEDIA_PATH}:/media -p 5050:5050 --rm imdevinc/couchpotato

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

RUN groupadd -r -g 666 couchpotato \
    && useradd -r -u 666 -g 666 -ms /bin/false couchpotato \
    && chown couchpotato:couchpotato /usr/src/couchpotato

RUN pip install \
        lxml \
        pyopenssl

EXPOSE 5050

ENV CP_VERSION master

USER couchpotato
RUN git clone https://github.com/CouchPotato/CouchPotatoServer.git /usr/src/couchpotato \
    && cd /usr/src/couchpotato \
    && git checkout "${CP_VERSION}"

ENTRYPOINT ["python", "CouchPotato.py"]
CMD ["--data_dir", "/data", "--console_log"]