import botocore
import boto3
from datetime import datetime, timezone, timedelta
from osc_bsu_backup.utils import setup_logging
from osc_bsu_backup.error import InputError

logger = setup_logging(__name__)

DESCRIPTION = "osc-bsu-backup EF50CF3A80164A5EABAF8C78B2314C65"
OLD_DESCRIPTION = ["osc-bsu-backup 0.1", "osc-bsu-backup 0.0.2", "osc-bsu-backup 0.0.1"]


def auth(profile, region, client_cert=None, endpoint=None):
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
    if client_cert:
        conn = session.client(
            "ec2",
            region_name=region,
            endpoint_url=endpoint,
            config=botocore.config.Config(client_cert=client_cert),
        )
    else:
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

    volumes = []
    filters = [
        {"Name": "instance-state-name", "Values": ["running", "stopped"]},
    ]

    for tag in tags:
        tag_key = tag.split(":")[0]
        tag_value = tag.split(":")[1]
        filters.append({"Name": "tag:{}".format(tag_key), "Values": [tag_value]})

    reservations = conn.describe_instances(Filters=filters)

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

    volumes = []
    filters = []

    for tag in tags:
        tag_key = tag.split(":")[0]
        tag_value = tag.split(":")[1]
        filters.append({"Name": "tag:{}".format(tag_key), "Values": [tag_value]})

    vol = conn.describe_volumes(Filters=filters)

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


def rotate_snapshots(conn, volumes, rotate=10, rotate_only=False):
    logger.info("rotate_snapshot: %d", rotate)
    del_snaps = []

    for vol in volumes:
        filters = [{"Name": "volume-id", "Values": [vol]}]
        if rotate_only:
            filters.append(
                {"Name": "description", "Values": [DESCRIPTION] + OLD_DESCRIPTION}
            )
        snaps = conn.describe_snapshots(Filters=filters)

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


def rotate_days_snapshots(conn, volumes, rotate=10, rotate_only=False):
    logger.info("rotate_snapshot: older than %d days", rotate)
    del_snaps = []

    for vol in volumes:
        filters = [{"Name": "volume-id", "Values": [vol]}]
        if rotate_only:
            filters.append(
                {"Name": "description", "Values": [DESCRIPTION] + OLD_DESCRIPTION}
            )
        snaps = conn.describe_snapshots(Filters=filters)

        if len(snaps["Snapshots"]) >= rotate and rotate >= 1:
            snaps["Snapshots"].sort(key=lambda x: x["StartTime"], reverse=True)

            for snap in snaps["Snapshots"]:
                if (datetime.now(timezone.utc) - snap["StartTime"]).days >= rotate:
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


def create_snapshots(conn, volumes, copy_tags=False):
    logger.info("create_snapshot")

    snaps = []

    for vol in volumes:
        snap = conn.create_snapshot(Description=DESCRIPTION, VolumeId=vol)

        logger.info("snap create: %s %s", vol, snap["SnapshotId"])
        snaps.append(snap)

        if copy_tags:
            vol_tags = conn.describe_volumes(VolumeIds=[vol])["Volumes"][0]["Tags"]
            conn.create_tags(Resources=[snap["SnapshotId"]], Tags=vol_tags)
            logger.info("copy of %s tags to %s", vol, snap["SnapshotId"])

    logger.info("wait for snapshots: %s", [i["SnapshotId"] for i in snaps])
    waiter = conn.get_waiter("snapshot_completed")
    waiter.wait(SnapshotIds=[i["SnapshotId"] for i in snaps])
