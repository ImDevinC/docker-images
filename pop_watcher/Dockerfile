FROM python:3-alpine

VOLUME ["/data"]
WORKDIR /usr/src/app

COPY . .
RUN pip install -r requirements.txt

ENV WEBHOOK_URL=
ENV CHALICE_CHECK_DELAY=
ENV BATCHES_PER_MINUTE=

ENTRYPOINT [ "python", "main.py"]