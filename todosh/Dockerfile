# Docker command:
#   docker run -it -v ${TODO_FOLDER}:/todos imdevinc/todosh

FROM alpine:latest
LABEL maintainer Devin Collins <me@imdevinc.com>
WORKDIR /usr/src/app
RUN apk add --no-cache \
    git \
    alpine-sdk \
    shadow \
    bash \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/todotxt/todo.txt-cli.git . \
    && git checkout master \
    && make \
    && make install \
    && useradd -r -ms /bin/bash todosh

USER todosh
COPY todo.cfg /etc/todo.cfg
ENTRYPOINT [ "todo.sh", "-d", "/etc/todo.cfg" ]
