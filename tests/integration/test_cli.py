import unittest
import logging
from unittest.mock import patch
import osc_bsu_backup.cli as cli
import osc_bsu_backup.bsu_backup as bsu_backup
import boto3
import botocore
import sys
import warnings


class TestIntegrationMethods(unittest.TestCase):
    def setUp(self):
        warnings.filterwarnings(
            "ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>"
        )
        self.region = "eu-west-2"
        endpoint = "https://fcu.eu-west-2.outscale.com"

        session = boto3.Session()
        self.conn = session.client(
            "ec2", region_name=self.region, endpoint_url=endpoint
        )

        self.tearDown()

        self.conn.create_key_pair(KeyName="osc_bsu_backup_27aaade4")
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        try:
            self.conn.delete_key_pair(KeyName="osc_bsu_backup_27aaade4")
        except botocore.exceptions.ClientError:
            pass

        vol = self.conn.describe_volumes(
            Filters=[
                {"Name": "tag:Name", "Values": ["osc_bsu_backup_27aaade4"]},
                {"Name": "status", "Values": ["available"]},
            ]
        )
        for i in vol["Volumes"]:
            self.conn.delete_volume(VolumeId=i["VolumeId"])

        snaps = self.conn.describe_snapshots(
            Filters=[{"Name": "description", "Values": ["osc_bsu_backup_27aaade4"]}]
        )
        for i in snaps["Snapshots"]:
            self.conn.delete_snapshot(SnapshotId=i["SnapshotId"])

        vms = self.conn.describe_instances(
            Filters=[
                {"Name": "tag:Name", "Values": ["osc_bsu_backup_27aaade4"]},
                {"Name": "instance-state-name", "Values": ["running"]},
            ]
        )
        for reservation in vms["Reservations"]:
            if reservation.get("Instances"):
                for instance in reservation["Instances"]:
                    self.conn.terminate_instances(InstanceIds=[instance["InstanceId"]])
                    self.conn.stop_instances(
                        InstanceIds=[instance["InstanceId"]], Force=True
                    )

        logging.disable(logging.NOTSET)

    def setUpVolumes(self):
        self.vol1 = self.conn.create_volume(
            AvailabilityZone=self.region + "a", Size=10, VolumeType="standard"
        )
        self.conn.get_waiter("volume_available").wait(VolumeIds=[self.vol1["VolumeId"]])
        self.conn.create_tags(
            Resources=[self.vol1["VolumeId"]],
            Tags=[
                {"Key": "Name", "Value": "osc_bsu_backup_27aaade4"},
                {"Key": "test2", "Value": "osc_bsu_backup_27aaade4"},
            ],
        )

        self.vol2 = self.conn.create_volume(
            AvailabilityZone=self.region + "a", Size=10, VolumeType="standard"
        )
        self.conn.get_waiter("volume_available").wait(VolumeIds=[self.vol2["VolumeId"]])
        self.conn.create_tags(
            Resources=[self.vol2["VolumeId"]],
            Tags=[
                {"Key": "Name", "Value": "osc_bsu_backup_27aaade4"},
                {"Key": "test2", "Value": "osc_bsu_backup_27aaade4"},
            ],
        )

    def setUpInstances(self, count=1):
        centos = self.conn.describe_images(
            Filters=[
                {"Name": "owner-alias", "Values": ["Outscale"]},
                {"Name": "name", "Values": ["CentOS-*"]},
            ]
        )

        self.vm1 = self.conn.run_instances(
            InstanceType="tinav4.c1r1p3",
            ImageId=centos["Images"][0]["ImageId"],
            KeyName="osc_bsu_backup_27aaade4",
            MinCount=1,
            MaxCount=count,
        )

        self.conn.get_waiter("instance_running").wait(
            InstanceIds=[i["InstanceId"] for i in self.vm1["Instances"]]
        )
        self.conn.create_tags(
            Resources=[i["InstanceId"] for i in self.vm1["Instances"]],
            Tags=[
                {"Key": "Name", "Value": "osc_bsu_backup_27aaade4"},
                {"Key": "test2", "Value": "osc_bsu_backup_27aaade4"},
            ],
        )

    def test_integration1(self):
        self.setUpVolumes()

        class args(object):
            volume_id = self.vol1["VolumeId"]
            instance_id = None
            instances_tags = None
            volumes_tags = None
            profile = "default"
            region = "eu-west-2"
            endpoint = None
            rotate = 1

        with patch("osc_bsu_backup.bsu_backup.DESCRIPTION", "osc_bsu_backup_27aaade4"):
            self.assertTrue(cli.backup(args()))
            snaps = self.conn.describe_snapshots(
                Filters=[{"Name": "description", "Values": ["osc_bsu_backup_27aaade4"]}]
            )
            self.assertEqual(len(snaps["Snapshots"]), 1)

            self.assertTrue(cli.backup(args()))
            snaps = self.conn.describe_snapshots(
                Filters=[{"Name": "description", "Values": ["osc_bsu_backup_27aaade4"]}]
            )
            self.assertEqual(len(snaps["Snapshots"]), 2)

            self.assertTrue(cli.backup(args()))
            snaps = self.conn.describe_snapshots(
                Filters=[{"Name": "description", "Values": ["osc_bsu_backup_27aaade4"]}]
            )
            self.assertEqual(len(snaps["Snapshots"]), 2)

    def test_integration2(self):
        self.setUpVolumes()

        class args(object):
            volume_id = None
            instance_id = None
            instances_tags = None
            volumes_tags = "test2:osc_bsu_backup_27aaade4"
            profile = "default"
            region = "eu-west-2"
            endpoint = None
            rotate = 1

        with patch("osc_bsu_backup.bsu_backup.DESCRIPTION", "osc_bsu_backup_27aaade4"):
            self.assertTrue(cli.backup(args()))
            snaps = self.conn.describe_snapshots(
                Filters=[{"Name": "description", "Values": ["osc_bsu_backup_27aaade4"]}]
            )
            self.assertEqual(len(snaps["Snapshots"]), 2)

            self.assertTrue(cli.backup(args()))
            snaps = self.conn.describe_snapshots(
                Filters=[{"Name": "description", "Values": ["osc_bsu_backup_27aaade4"]}]
            )
            self.assertEqual(len(snaps["Snapshots"]), 4)

            self.assertTrue(cli.backup(args()))
            snaps = self.conn.describe_snapshots(
                Filters=[{"Name": "description", "Values": ["osc_bsu_backup_27aaade4"]}]
            )
            self.assertEqual(len(snaps["Snapshots"]), 4)

    def test_integration3(self):
        self.setUpInstances(count=1)

        class args(object):
            volume_id = None
            instance_id = self.vm1["Instances"][0]["InstanceId"]
            instances_tags = None
            volumes_tags = None
            profile = "default"
            region = "eu-west-2"
            endpoint = None
            rotate = 1

        with patch("osc_bsu_backup.bsu_backup.DESCRIPTION", "osc_bsu_backup_27aaade4"):
            self.assertTrue(cli.backup(args()))
            snaps = self.conn.describe_snapshots(
                Filters=[{"Name": "description", "Values": ["osc_bsu_backup_27aaade4"]}]
            )
            self.assertEqual(len(snaps["Snapshots"]), 1)

            self.assertTrue(cli.backup(args()))
            snaps = self.conn.describe_snapshots(
                Filters=[{"Name": "description", "Values": ["osc_bsu_backup_27aaade4"]}]
            )
            self.assertEqual(len(snaps["Snapshots"]), 2)

            self.assertTrue(cli.backup(args()))
            snaps = self.conn.describe_snapshots(
                Filters=[{"Name": "description", "Values": ["osc_bsu_backup_27aaade4"]}]
            )
            self.assertEqual(len(snaps["Snapshots"]), 2)

    def test_integration4(self):
        self.setUpInstances(count=4)

        class args(object):
            volume_id = None
            instance_id = None
            instances_tags = "test2:osc_bsu_backup_27aaade4"
            volumes_tags = None
            profile = "default"
            region = "eu-west-2"
            endpoint = None
            rotate = 1

        with patch("osc_bsu_backup.bsu_backup.DESCRIPTION", "osc_bsu_backup_27aaade4"):
            self.assertTrue(cli.backup(args()))
            snaps = self.conn.describe_snapshots(
                Filters=[{"Name": "description", "Values": ["osc_bsu_backup_27aaade4"]}]
            )
            self.assertEqual(len(snaps["Snapshots"]), 4)

            self.assertTrue(cli.backup(args()))
            snaps = self.conn.describe_snapshots(
                Filters=[{"Name": "description", "Values": ["osc_bsu_backup_27aaade4"]}]
            )
            self.assertEqual(len(snaps["Snapshots"]), 8)

            self.assertTrue(cli.backup(args()))
            snaps = self.conn.describe_snapshots(
                Filters=[{"Name": "description", "Values": ["osc_bsu_backup_27aaade4"]}]
            )
            self.assertEqual(len(snaps["Snapshots"]), 8)


if __name__ == "__main__":
    unittest.main()
