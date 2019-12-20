import argparse
import logging
from osc_bsu_backup.bsu_backup import BsuBackup
from osc_bsu_backup.utils import setup_logging

from osc_bsu_backup import __version__

logger = setup_logging(__name__)


def main():
    logger.info("osc_bsu_backup: %s", __version__)

    parser = argparse.ArgumentParser(
        description="osc-ebs-backup: {}".format(__version__)
    )
    parser.add_argument(
        "--instance-by-id",
        dest="instance_id",
        action="store",
        help="instance to backup",
    )
    parser.add_argument(
        "--instance-by-tags",
        dest="instance_tags",
        action="store",
        help="instances tags to look for use the format Key:Value",
    )
    parser.add_argument(
        "--rotate",
        dest="rotate",
        type=int,
        action="store",
        default=10,
        help="retention for snapshot",
    )
    parser.add_argument(
        "--region", dest="region", action="store", default="eu-west-2", help="region"
    )
    parser.add_argument(
        "--endpoint", dest="endpoint", default=None, action="store", help="endpoint"
    )
    parser.add_argument(
        "--profile", dest="profile", action="store", default="default", help="profile"
    )
    parser.add_argument(
        "--debug", dest="debug", action="store_true", default=False, help="enable debug"
    )
    args = parser.parse_args()

    if args.instance_tags and len(args.instance_tags.split(":")) != 2:
        parser.error(
            "please use the format Key:Value for tags: --instance-by-tags Name:vm-1"
        )
    elif not args.instance_id and not args.instance_tags:
        parser.error("please use --instance-by-id or --instance-by-tags")

    if args.debug:
        setup_logging(level=logging.DEBUG)

    back = BsuBackup(args.profile, args.region, args.endpoint)

    back.auth()

    if args.instance_id:
        res = back.find_instance_by_id(args.instance_id)
    elif args.instance_tags:
        res = back.find_instances_by_tags(args.instance_tags)

    back.rotate_snapshots(res, args.rotate)

    back.create_snapshots(res)


if __name__ == "__main__":
    main()
