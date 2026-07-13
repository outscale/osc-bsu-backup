FROM python:3.7@sha256:eedf63967cdb57d8214db38ce21f105003ed4e4d0358f02bedc057341bcf92a0

MAINTAINER Rémi Jouannet "remi.jouannet@outscale.com"

WORKDIR /root/osc-bsu-backup
COPY ./ /root/osc-bsu-backup

RUN make clean
RUN make develop

ENTRYPOINT ["make"]
