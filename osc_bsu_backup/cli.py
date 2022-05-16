import argparse
import logging
import osc_bsu_backup.bsu_backup as bsu_backup
from osc_bsu_backup.utils import setup_logging

from osc_bsu_backup import __version__

logger = setup_logging(__name__)


def backup(args):
    conn = bsu_backup.auth(args.profile, args.region, args.client_cert, args.endpoint)

    if args.instance_id:
        res = bsu_backup.find_instance_by_id(conn, args.instance_id)
    elif args.instances_tags:
        res = bsu_backup.find_instances_by_tags(conn, args.instances_tags)
    elif args.volume_id:
        res = bsu_backup.find_volume_by_id(conn, args.volume_id)
    elif args.volumes_tags:
        res = bsu_backup.find_volumes_by_tags(conn, args.volumes_tags)

    if res:
        if args.rotate_days:
            bsu_backup.rotate_days_snapshots(
                conn, res, args.rotate_days, args.rotate_only
            )
        elif args.rotate:
            bsu_backup.rotate_snapshots(conn, res, args.rotate, args.rotate_only)
        else:
            bsu_backup.rotate_snapshots(conn, res, 10, args.rotate_only)

        bsu_backup.create_snapshots(conn, res, args.copy_tags)


def main():
    logger.info("osc_bsu_backup: %s", __version__)

    parser = argparse.ArgumentParser(
        description="osc-bsu-backup: {}".format(__version__)
    )
    parser.add_argument(
        "--instance-by-id",
        dest="instance_id",
        action="store",
        help="instance to backup",
    )
    parser.add_argument(
        "--instances-by-tags",
        dest="instances_tags",
        action="store",
        nargs="+",
        help="instances tags to look for, use the format Key:Value. Can be used multiple times",
    )
    parser.add_argument(
        "--volume-by-id",
        dest="volume_id",
        action="store",
        help="volume to backup",
    )
    parser.add_argument(
        "--volumes-by-tags",
        dest="volumes_tags",
        action="store",
        nargs="+",
        help="volumes tags to look for, use the format Key:Value. Can be used multiple times",
    )
    parser.add_argument(
        "--rotate",
        dest="rotate",
        type=int,
        action="store",
        default=None,
        help="retention for snapshot",
    )
    parser.add_argument(
        "--rotate-by-days",
        dest="rotate_days",
        type=int,
        action="store",
        default=None,
        help="retention for snapshot, delete snapshots if there are older than N days",
    )
    parser.add_argument(
        "--rotate-only",
        dest="rotate_only",
        action="store_true",
        default=False,
        help="only rotate snapshots create by osc-bsu-backup",
    )
    parser.add_argument(
        "--copy-tags",
        dest="copy_tags",
        action="store_true",
        default=False,
        help="copy the volume tags to the created snapshots",
    )
    parser.add_argument(
        "--region", dest="region", action="store", default="eu-west-2", help="region"
    )
    parser.add_argument(
        "--endpoint", dest="endpoint", default=None, action="store", help="endpoint"
    )
    parser.add_argument(
        "--profile",
        dest="profile",
        action="store",
        default=None,
        help="aws profile to use, ~/.aws/credentials. Don't set to use environment variables",
    ),
    parser.add_argument(
        "--client-cert",
        dest="client_cert",
        action="store",
        default=None,
        help="for TLS client authentication",
    )
    parser.add_argument(
        "--debug", dest="debug", action="store_true", default=False, help="enable debug"
    )
    args = parser.parse_args()

    if args.instances_tags:
        for tag in args.instances_tags:
            if len(tag.split(":")) != 2:
                parser.error(
                    "please use the format Key:Value for tags: --instances-by-tags Name:vm-1"
                )
    elif args.volumes_tags:
        for tag in args.volumes_tags:
            if len(tag.split(":")) != 2:
                parser.error(
                    "please use the format Key:Value for tags: --volumes-by-tags Name:vm-1"
                )
    elif (
        not args.instance_id
        and not args.instances_tags
        and not args.volume_id
        and not args.volumes_tags
    ):
        parser.error(
            "please use --instance-by-id or --instances-by-tags or --volume-by-id or --volumes-by-tags"
        )
    elif args.rotate and args.rotate_days:
        parser.error("you can't use rotate and rotate-by-days")

    if args.debug:
        setup_logging(level=logging.DEBUG)

    return backup(args)


if __name__ == "__main__":
    main()
