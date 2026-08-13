FROM python:3.12@sha256:dd4fe98ab39f91e936f8e7e7a65a3ce59ecfb11e32f9a125b3132779920ba7f7

MAINTAINER Rémi Jouannet "remi.jouannet@outscale.com"

WORKDIR /root/osc-bsu-backup
COPY ./ /root/osc-bsu-backup

RUN make clean
RUN make develop

ENTRYPOINT ["make"]
