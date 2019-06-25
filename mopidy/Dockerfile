FROM ubuntu:latest

RUN apt-get update && \
    apt-get install -y gnupg2 wget git

RUN wget -q -O - https://apt.mopidy.com/mopidy.gpg | apt-key add - && \
    wget -q -O /etc/apt/sources.list.d/mopidy.list https://apt.mopidy.com/stretch.list

RUN apt-get update && \
    apt-get install -y mopidy python-pip python-dev

WORKDIR /tmp
RUN git clone https://github.com/mopidy/mopidy-gmusic.git
WORKDIR /tmp/mopidy-gmusic
RUN python setup.py build && \
    python setup.py install && \
    pip install Mopidy-Moped

COPY mopidy.conf /root/.config/mopidy/mopidy.conf

ENTRYPOINT [ "mopidy" ]
