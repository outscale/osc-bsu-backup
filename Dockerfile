FROM python:3.6

MAINTAINER Rémi Jouannet "remi.jouannet@outscale.com"

WORKDIR /root/osc-bsu-backup
COPY ./ /root/osc-bsu-backup

ENTRYPOINT ["make"]
