import botocore
import boto3
from osc_bsu_backup.utils import setup_logging
from osc_bsu_backup.error import InputError

from osc_bsu_backup import __version__

logger = setup_logging(__name__)


def auth(profile, region, endpoint=None):
    default_region = ["us-east-2", "eu-west-2", "cn-southeast-1", "us-west-1"]

    if not endpoint and region in default_region:
        if region == "cn-southeast-1":
            endpoint = "https://fcu.{}.outscale.hk".format(region)
        else:
            endpoint = "https://fcu.{}.outscale.com".format(region)
    elif not endpoint and region not in default_region:
        raise InputError(
            "You must specify an endpoint when the region is not : {}".format(
                default_region
            )
        )
    else:
        endpoint = endpoint

    logger.info("region: {}".format(region))
    logger.info("endpoint: {}".format(endpoint))
    logger.info("profile: {}".format(profile))

    logger.info("authenticate: %s %s", region, endpoint)

    session = boto3.Session(profile_name=profile)
    conn = session.client("ec2", region_name=region, endpoint_url=endpoint)

    logger.info(type(session))
    logger.info(type(conn))
    logger.info(conn.describe_key_pairs()["KeyPairs"][0])

    return conn


def find_instance_by_id(conn, id):
    logger.info("find the instance by id: %s", id)

    reservations = conn.describe_instances(InstanceIds=[id])

    if reservations:
        for reservation in reservations["Reservations"]:
            for instance in reservation["Instances"]:
                logger.info(
                        "instance found: %s %s", instance["InstanceId"], instance["Tags"]
                        )

    return reservations

def find_instances_by_tags(conn, tags):
    logger.info("find the instance by tags: %s", tags)
    tag_key = tags.split(":")[0]
    tag_value = tags.split(":")[1]

    reservations = conn.describe_instances(
        Filters=[{"Name": "tag:{}".format(tag_key), "Values": [tag_value]}]
    )

    if reservations:
        for reservation in reservations["Reservations"]:
            for instance in reservation["Instances"]:
                logger.info(
                        "instance found: %s %s", instance["InstanceId"], instance["Tags"]
                        )

    return reservations


def find_volumes(res):
    for reservation in res["Reservations"]:
        for instance in reservation["Instances"]:
            for vol in instance["BlockDeviceMappings"]:
                logger.info(
                    "volume found: %s %s",
                    instance["InstanceId"],
                    vol["Ebs"]["VolumeId"],
                )
                yield vol["Ebs"]["VolumeId"]


def rotate_snapshots(conn, res, rotate=10):
    logger.info("rotate_snapshot: %d", rotate)
    del_snaps = []

    for vol in find_volumes(res):
        snaps = conn.describe_snapshots(
            Filters=[{"Name": "volume-id", "Values": [vol]}]
        )

        if len(snaps["Snapshots"]) > rotate:
            snaps["Snapshots"].sort(key=lambda x: x["StartTime"], reverse=True)

            for i, snap in enumerate(snaps["Snapshots"], start=0):
                if i > rotate:
                    logger.info(
                        "deleting this snap: %s %s %s",
                        vol,
                        snap["SnapshotId"],
                        snap["StartTime"].strftime("%m/%d/%Y, %H:%M:%S"),
                    )

                    try:
                        del_snap = conn.delete_snapshot(SnapshotId=snap["SnapshotId"])
                    except botocore.exceptions.ClientError as e:
                        if e.response["Error"]["Code"] == "InvalidSnapshot.InUse":
                            logger.error(e)
                        else:
                            raise e
                else:
                    logger.info(
                        "snaps to keep: %s %s %s",
                        vol,
                        snap["SnapshotId"],
                        snap["StartTime"].strftime("%m/%d/%Y, %H:%M:%S"),
                    )


def create_snapshots(conn, res):
    logger.info("create_snapshot")

    snaps = []

    for vol in find_volumes(res):
        snap = conn.create_snapshot(
            Description="osc-bsu-backup {}".format(__version__), VolumeId=vol
        )

        logger.info("snap create: %s %s", vol, snap["SnapshotId"])
        snaps.append(snap)

    logger.info("wait for snapshots: %s", [i["SnapshotId"] for i in snaps])
    waiter = conn.get_waiter("snapshot_completed")
    waiter.wait(SnapshotIds=[i["SnapshotId"] for i in snaps])
