# Docker run command:
#   docker run -v $(PWD)/plex-net.conf:/etc/nginx/conf.d/plex-net.conf -p 80:80 --rm --network plex-net imdevinc/nginx-plex-net 

FROM alpine:latest
LABEL maintainer Devin Collins <me@imdevinc.com>

WORKDIR /usr/src/app
RUN apk add --no-cache \
    nginx \
    && rm -f /etc/nginx/conf.d/default.conf \
    && mkdir -p /run/nginx
RUN ln -sf /dev/stdout /var/log/nginx/access.log \ && ln -sf /dev/stderr /var/log/nginx/error.log
COPY conf.d/* /etc/nginx/conf.d/

ENTRYPOINT [ "nginx", "-g", "daemon off;" ]
