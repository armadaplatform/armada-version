FROM microservice_python3.5
MAINTAINER Cerebro <cerebro@ganymede.eu>

RUN pip3.5 install -U armada tornado==4.3

ENV CONFIG_DIR ./config

ADD . /opt/armada-version
ADD ./supervisor/armada-version.conf /etc/supervisor/conf.d/armada-version.conf

EXPOSE 80
