import unittest
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
        region = "eu-west-2"
        endpoint = "https://fcu.eu-west-2.outscale.com"

        session = boto3.Session()
        self.conn = session.client("ec2", region_name=region, endpoint_url=endpoint)

        self.tearDown()

        conn = self.conn

        conn.create_key_pair(KeyName="osc_bsu_backup_27aaade4")

        self.vol1 = conn.create_volume(
            AvailabilityZone=region + "a", Size=10, VolumeType="standard"
        )
        conn.get_waiter("volume_available").wait(VolumeIds=[self.vol1["VolumeId"]])
        conn.create_tags(
            Resources=[self.vol1["VolumeId"]],
            Tags=[{"Key": "Name", "Value": "osc_bsu_backup_27aaade4"}, 
                {"Key": "test2", "Value" : "osc_bsu_backup_27aaade4"}],
        )

        self.vol2 = conn.create_volume(
            AvailabilityZone=region + "a", Size=10, VolumeType="standard"
        )
        conn.get_waiter("volume_available").wait(VolumeIds=[self.vol2["VolumeId"]])
        conn.create_tags(
            Resources=[self.vol2["VolumeId"]],
            Tags=[{"Key": "Name", "Value": "osc_bsu_backup_27aaade4"}, 
                {"Key": "test2", "Value" : "osc_bsu_backup_27aaade4"}],
        )

    def tearDown(self):
        conn = self.conn

        try:
            conn.delete_key_pair(KeyName="osc_bsu_backup_27aaade4")
        except botocore.exceptions.ClientError:
            pass

        vol = conn.describe_volumes(
            Filters=[{"Name": "tag:Name", "Values": ["osc_bsu_backup_27aaade4"]}]
        )
        for i in vol["Volumes"]:
            conn.delete_volume(VolumeId=i["VolumeId"])

        snaps = conn.describe_snapshots(
            Filters=[{"Name": "description", "Values": ["osc_bsu_backup_27aaade4"]}]
        )
        for i in snaps["Snapshots"]:
            conn.delete_snapshot(SnapshotId=i["SnapshotId"])

        vms = conn.describe_instances(
            Filters=[{"Name": "tag:Name", "Values": ["osc_bsu_backup_27aaade4"]}]
        )
        for reservation in vms["Reservations"]:
            if reservation.get('Instances'):
                for instance in reservation["Instances"]:
                    conn.terminate_instances(InstanceId=instance["InstanceId"])

    def test_integration1(self):
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

if __name__ == "__main__":
    unittest.main()
