import botocore
import boto3
from osc_bsu_backup.utils import setup_logging
from osc_bsu_backup.error import InputError

from osc_bsu_backup import __version__

logger = setup_logging(__name__)

DESCRIPTION = "osc-bsu-backup {}".format(__version__)


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

    logger.info(conn.describe_key_pairs()["KeyPairs"][0])

    return conn


def find_instance_by_id(conn, id):
    logger.info("find the instance by id: %s", id)

    volumes = []
    reservations = conn.describe_instances(InstanceIds=[id])

    if reservations:
        for reservation in reservations["Reservations"]:
            for instance in reservation["Instances"]:
                logger.info(
                    "instance found: %s %s", instance["InstanceId"], instance["Tags"]
                )
                for vol in instance["BlockDeviceMappings"]:
                    logger.info(
                        "volume found: %s %s",
                        instance["InstanceId"],
                        vol["Ebs"]["VolumeId"],
                    )
                    volumes.append(vol["Ebs"]["VolumeId"])
    else:
        logger.warning("instance not found: %s", id)

    return volumes


def find_instances_by_tags(conn, tags):
    logger.info("find the instance by tags: %s", tags)
    tag_key = tags.split(":")[0]
    tag_value = tags.split(":")[1]
    volumes = []

    reservations = conn.describe_instances(
        Filters=[
            {"Name": "tag:{}".format(tag_key), "Values": [tag_value]},
            {"Name": "instance-state-name", "Values": ["running", "stopped"]},
        ]
    )

    if reservations:
        for reservation in reservations["Reservations"]:
            for instance in reservation["Instances"]:
                logger.info(
                    "instance found: %s %s", instance["InstanceId"], instance["Tags"]
                )
                for vol in instance["BlockDeviceMappings"]:
                    logger.info(
                        "volume found: %s %s",
                        instance["InstanceId"],
                        vol["Ebs"]["VolumeId"],
                    )
                    volumes.append(vol["Ebs"]["VolumeId"])
    else:
        logger.warning("instances not found: %s", tags)

    return volumes


def find_volumes_by_tags(conn, tags):
    logger.info("find the volume by tags: %s", tags)
    tag_key = tags.split(":")[0]
    tag_value = tags.split(":")[1]
    volumes = []

    vol = conn.describe_volumes(
        Filters=[{"Name": "tag:{}".format(tag_key), "Values": [tag_value]}]
    )

    if len(vol["Volumes"]) != 0:
        for vol in vol["Volumes"]:
            logger.info("volume found: %s %s", vol["VolumeId"], vol["Tags"])
            volumes.append(vol["VolumeId"])
    else:
        logger.warning("volumes not found: %s", tags)

    return volumes


def find_volume_by_id(conn, id):
    logger.info("find the volume by id: %s", id)

    volumes = []
    vol = conn.describe_volumes(VolumeIds=[id])

    if len(vol["Volumes"]) != 0:
        for vol in vol["Volumes"]:
            logger.info("volume found: %s %s", vol["VolumeId"], vol["Tags"])
            volumes.append(vol["VolumeId"])
    else:
        logger.warning("volumes not found: %s", id)

    return volumes


def rotate_snapshots(conn, volumes, rotate=10):
    logger.info("rotate_snapshot: %d", rotate)
    del_snaps = []

    for vol in volumes:
        snaps = conn.describe_snapshots(
            Filters=[
                {"Name": "volume-id", "Values": [vol]},
                {"Name": "description", "Values": [DESCRIPTION]},
            ]
        )

        if len(snaps["Snapshots"]) >= rotate and rotate >= 1:
            snaps["Snapshots"].sort(key=lambda x: x["StartTime"], reverse=True)

            for i, snap in enumerate(snaps["Snapshots"], start=0):
                if i >= rotate:
                    logger.info(
                        "deleting this snap: %s %s %s",
                        vol,
                        snap["SnapshotId"],
                        str(snap["StartTime"]),
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
                        str(snap["StartTime"]),
                    )


def create_snapshots(conn, volumes):
    logger.info("create_snapshot")

    snaps = []

    for vol in volumes:
        snap = conn.create_snapshot(Description=DESCRIPTION, VolumeId=vol)

        logger.info("snap create: %s %s", vol, snap["SnapshotId"])
        snaps.append(snap)

    logger.info("wait for snapshots: %s", [i["SnapshotId"] for i in snaps])
    waiter = conn.get_waiter("snapshot_completed")
    waiter.wait(SnapshotIds=[i["SnapshotId"] for i in snaps])
