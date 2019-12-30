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

## Usage

```bash
/usr/local/outscale/virtualenv/bin/osc-bsu-backup --help
INFO:osc_bsu_backup.cli:osc_bsu_backup: 0.0.1
usage: osc-bsu-backup [-h] [--instance-by-id INSTANCE_ID]
                      [--instance-by-tags INSTANCE_TAGS] [--rotate ROTATE]
                      [--region REGION] [--endpoint ENDPOINT]
                      [--profile PROFILE] [--debug]
 
osc-ebs-backup: 0.0.1
 
optional arguments:
  -h, --help            show this help message and exit
  --instance-by-id INSTANCE_ID
                        instance to backup
  --instance-by-tags INSTANCE_TAGS
                        instances tags to look for, use the format Key:Value
  --rotate ROTATE       retention for snapshot
  --region REGION       region
  --endpoint ENDPOINT   endpoint
  --profile PROFILE     aws profile to use
  --debug               enable debug
```

## How to use

this tool is intend to be use with cron and aws profile, here is an example of setup

this cron will backup every instance that has the tag autosnapshot=Yes
it will only keep the seventh more recent snapshots

```bash
#crontab -l
5 2 * * * osc-bsu-backup --profile default --region eu-west-2 --rotate 7 --instance-by-tags 'autosnapshot:Yes'
```

```bash
#~/.aws/credentials
[default]
aws_access_key_id = NABUAZEYBFZEBAZF6554631
aws_secret_access_key = AIGFABUIBZF10354AZF3A1CZ53A
```

