# Docker run command:
#   docker run -v $(PWD)/plex-net.conf:/etc/nginx/conf.d/plex-net.conf -p 80:80 --rm --network plex-net imdevinc/nginx-plex-net 

FROM alpine:latest
LABEL maintainer Devin Collins <me@imdevinc.com>

WORKDIR /usr/src/app
RUN apk add --no-cache \
    nginx \
    && rm -f /etc/nginx/conf.d/default.conf \
    && mkdir -p /run/nginx
COPY plex-net.conf /etc/nginx/conf.d/plex-net.conf

ENTRYPOINT [ "nginx", "-g", "daemon off;" ]
