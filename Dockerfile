FROM python:3.7

MAINTAINER Rémi Jouannet "remi.jouannet@outscale.com"

WORKDIR /root/osc-bsu-backup
COPY ./ /root/osc-bsu-backup

RUN make clean
RUN make develop

ENTRYPOINT ["make"]
