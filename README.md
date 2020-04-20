# osc-bsu-backup

## Introduction

cli tool to easily schedule instance snapshots and rotate it on Outscale Cloud

## Install

```bash
python3 setup.py install
```

## How to build

```bash
make develop
```

## How to tests

```bash
make unit
```

```bash
#you must have an account on the region eu-west-2 from Outscale
#~/.aws/credentials
[default]
aws_access_key_id = NABUAZEYBFZEBAZF6554631
aws_secret_access_key = AIGFABUIBZF10354AZF3A1CZ53A

make integration
```

## Usage

```bash
INFO:osc_bsu_backup.cli:osc_bsu_backup: 0.0.2
usage: osc-bsu-backup [-h] [--instance-by-id INSTANCE_ID]
                      [--instances-by-tags INSTANCES_TAGS]
                      [--volume-by-id VOLUME_ID]
                      [--volumes-by-tags VOLUMES_TAGS] [--rotate ROTATE]
                      [--region REGION] [--endpoint ENDPOINT]
                      [--profile PROFILE] [--debug]

osc-ebs-backup: 0.0.2

optional arguments:
  -h, --help            show this help message and exit
  --instance-by-id INSTANCE_ID
                        instance to backup
  --instances-by-tags INSTANCES_TAGS
                        instances tags to look for, use the format Key:Value
  --volume-by-id VOLUME_ID
                        volume to backup
  --volumes-by-tags VOLUMES_TAGS
                        volumes tags to look for, use the format Key:Value
  --rotate ROTATE       retention for snapshot
  --region REGION       region
  --endpoint ENDPOINT   endpoint
  --profile PROFILE     aws profile to use, ~/.aws/credentials
  --debug               enable debug
```

## How to use

this tool is intend to be use with cron and aws profile, here is an example of setup

this cron will backup every instance that has the tag autosnapshot=Yes
it will only keep the seventh more recent snapshots

```bash
#crontab -l
5 2 * * * osc-bsu-backup --profile default --region eu-west-2 --rotate 7 --instances-by-tags 'autosnapshot:Yes'
```

```bash
#~/.aws/credentials
[default]
aws_access_key_id = NABUAZEYBFZEBAZF6554631
aws_secret_access_key = AIGFABUIBZF10354AZF3A1CZ53A
```

