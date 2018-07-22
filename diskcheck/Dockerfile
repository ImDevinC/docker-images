# Run command:
#   docker run -d -e USER_TOKEN=${USER_TOKEN} -e APP_TOKEN=${APP_TOKEN} -v ${MOUNTED_PARTITION}:/mnt/data --rm -h diskcheck imdevinc/diskcheck

FROM alpine:latest
LABEL maintainer Devin Collins <me@imdevinc.com>
WORKDIR /usr/src/app

COPY diskcheck.py .

RUN apk add --no-cache \
    python \
    shadow \
    py-pip \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -r -ms /bin/false diskchecker \
    && pip install requests \
    && chown -R diskchecker:diskchecker /usr/src/app

USER diskchecker
ENTRYPOINT ["python", "diskcheck.py"]