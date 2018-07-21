# Docker command:
#   docker run -it -v ${TODO_FOLDER}:/todos -v ${CONFIG_FILE}:/todo.cfg -e TODOTXT_CFG_FILE=/todo.cfg imdevinc/todosh

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
RUN echo alias t="todo.sh" >> /home/todosh/.bashrc
ENTRYPOINT [ "bash" ]