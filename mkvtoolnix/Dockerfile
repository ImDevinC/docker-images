# Docker command:
#   docker run -it -v ${TODO_FOLDER}:/todos -v ${CONFIG_FILE}:/todo.cfg -e TODOTXT_CFG_FILE=/todo.cfg imdevinc/todosh

FROM alpine:latest
LABEL maintainer Devin Collins <me@imdevinc.com>
WORKDIR /usr/src/app
RUN apk add --no-cache \
    shadow \
    bash \
    mkvtoolnix \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -ms /bin/bash mkvtool

USER mkvtool
ENTRYPOINT [ "bash" ]
