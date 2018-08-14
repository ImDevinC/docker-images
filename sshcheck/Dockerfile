FROM alpine:latest
LABEL maintainer Devin Collins <me@imdevinc.com>
WORKDIR /usr/src/app

COPY sshcheck.py .
COPY requirements.txt .

RUN apk add --no-cache \
    python \
    py-pip \
    && rm -rf /var/lib/apt/lists/* \
    && pip install -r requirements.txt

ENTRYPOINT [ "python", "sshcheck.py" ]