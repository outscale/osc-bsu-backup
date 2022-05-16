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
aws_access_key_id = XXX_ACCESS_KEY_XXX
aws_secret_access_key = XXX_SECRET_KEY_XXX

make integration
```

## Usage

```bash
INFO:osc_bsu_backup.cli:osc_bsu_backup: 0.0.5
usage: osc-bsu-backup [-h] [--instance-by-id INSTANCE_ID] [--instances-by-tags INSTANCES_TAGS [INSTANCES_TAGS ...]] [--volume-by-id VOLUME_ID]
                      [--volumes-by-tags VOLUMES_TAGS [VOLUMES_TAGS ...]] [--rotate ROTATE] [--rotate-by-days ROTATE_DAYS] [--rotate-only] [--copy-tags]
                      [--region REGION] [--endpoint ENDPOINT] [--profile PROFILE] [--client-cert CLIENT_CERT] [--debug]

osc-bsu-backup: 0.0.5

optional arguments:
  -h, --help            show this help message and exit
  --instance-by-id INSTANCE_ID
                        instance to backup
  --instances-by-tags INSTANCES_TAGS [INSTANCES_TAGS ...]
                        instances tags to look for, use the format Key:Value. Can be used multiple times
  --volume-by-id VOLUME_ID
                        volume to backup
  --volumes-by-tags VOLUMES_TAGS [VOLUMES_TAGS ...]
                        volumes tags to look for, use the format Key:Value. Can be used multiple times
  --rotate ROTATE       retention for snapshot
  --rotate-by-days ROTATE_DAYS
                        retention for snapshot, delete snapshots if there are older than N days
  --rotate-only         only rotate snapshots create by osc-bsu-backup
  --copy-tags           copy the volume tags to the created snapshots
  --region REGION       region
  --endpoint ENDPOINT   endpoint
  --profile PROFILE     aws profile to use, ~/.aws/credentials. Don't set to use environment variables
  --client-cert CLIENT_CERT
                        for TLS client authentication
  --debug               enable debug
```

## How to use

this tool is intend to be use with cron and aws profile, here is an example of setup

this cron will backup every instance that has the tag autosnapshot=Yes
it will only keep the seventh more recent snapshots

```bash
#crontab -l
5 2 * * * osc-bsu-backup --profile default --region eu-west-2 --rotate 7 --instances-by-tags 'autosnapshot:Yes'
7 2 * * * osc-bsu-backup --profile default --region eu-west-2 --rotate 7 --client-cert /home/remi/test1.pem --instances-by-tags 'autosnapshot:Yes'
4 2 * * * osc-bsu-backup --profile default --region eu-west-2 --rotate 7 --client-cert /home/remi/test1.pem --instances-by-tags 'autosnapshot:Yes' --instances-by-tags 'Name:test1'
```

```bash
#~/.aws/credentials
[default]
aws_access_key_id = XXX_ACCESS_KEY_XXX
aws_secret_access_key = XXX_SECRET_KEY_XXX
```

Environment variables could be used for authentication instead of aws profile. Set these environment variables (the `--profile` option should not be set):

```
AWS_ACCESS_KEY_ID=XXX_ACCESS_KEY_XXX
AWS_SECRET_ACCESS_KEY=XXX_SECRET_KEY_XXX
```

## Eim policy

```json
{
    "Statement": [
        {
            "Action": [
                "ec2:DescribeKeyPairs"
            ],
            "Resource": [
                "*"
            ],
            "Effect": "Allow"
        },
        {
            "Action": [
                "ec2:CreateSnapshot"
            ],
            "Resource": [
                "*"
            ],
            "Effect": "Allow"
        },
        {
            "Action": [
                "ec2:DescribeInstances"
            ],
            "Resource": [
                "*"
            ],
            "Effect": "Allow"
        },
        {
            "Action": [
                "ec2:DescribeVolumes"
            ],
            "Resource": [
                "*"
            ],
            "Effect": "Allow"
        },
        {
            "Action": [
                "ec2:DescribeSnapshots"
            ],
            "Resource": [
                "*"
            ],
            "Effect": "Allow"
        },
        {
            "Action": [
                "ec2:DeleteSnapshot"
            ],
            "Resource": [
                "*"
            ],
            "Effect": "Allow"
        }
    ]
}
```
