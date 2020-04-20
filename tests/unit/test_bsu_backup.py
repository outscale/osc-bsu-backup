import unittest
import logging
from unittest.mock import patch
import boto3
import botocore.session
from botocore.stub import Stubber
import json
import os
import osc_bsu_backup.bsu_backup as bsu
from osc_bsu_backup.error import InputError
import tests.unit.fixtures_bsu_backup as fixtures
from osc_bsu_backup import __version__


class TestBsuBackup(unittest.TestCase):
    def setUp(self):
        self.ec2 = botocore.session.get_session().create_client("ec2")
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_auth1(self):
        with patch("boto3.Session"):
            self.assertTrue(
                bsu.auth(region="eu-west-2", profile="default", endpoint=None)
            )

        self.assertRaises(InputError, bsu.auth, "eu-west-3", "default", None)

    def test_auth2(self):
        self.assertRaises(InputError, bsu.auth, "eu-west-3", "default", None)

    def test_find_instance_by_id1(self):
        with Stubber(self.ec2) as stubber:
            stubber.add_response(
                "describe_instances",
                fixtures.instances,
                {"InstanceIds": ["i-e6b7ab04"]},
            )
            for i in bsu.find_instance_by_id(self.ec2, "i-e6b7ab04"):
                self.assertEqual(i, "vol-a87f91c1")

    def test_find_instance_by_id2(self):
        with Stubber(self.ec2) as stubber:
            stubber.add_response(
                "describe_instances", {}, {"InstanceIds": ["i-e6b7ab05"]}
            )
            for i in bsu.find_instance_by_id(self.ec2, "i-e6b7ab05"):
                self.assertEqual(i, None)

    def test_find_instances_by_tags1(self):
        with Stubber(self.ec2) as stubber:
            stubber.add_response(
                "describe_instances",
                fixtures.instances,
                {
                    "Filters": [
                        {"Name": "tag:Name", "Values": ["test1"]},
                        {
                            "Name": "instance-state-name",
                            "Values": ["running", "stopped"],
                        },
                    ]
                },
            )
            for i in bsu.find_instances_by_tags(self.ec2, "Name:test1"):
                self.assertEqual(i, "vol-a87f91c1")

    def test_find_volume_by_id1(self):
        with Stubber(self.ec2) as stubber:
            stubber.add_response(
                "describe_volumes", fixtures.volumes, {"VolumeIds": ["vol-a24fffdc"]}
            )
            for i in bsu.find_volume_by_id(self.ec2, "vol-a24fffdc"):
                self.assertEqual(i, "vol-a24fffdc")

    def test_find_volume_by_id2(self):
        with Stubber(self.ec2) as stubber:
            stubber.add_response(
                "describe_volumes", {"Volumes": []}, {"VolumeIds": ["vol-a24fffda"]}
            )
            for i in bsu.find_volume_by_id(self.ec2, "vol-a24fffda"):
                assertEqual(i, None)

    def test_find_volumes_by_tags1(self):
        with Stubber(self.ec2) as stubber:
            stubber.add_response(
                "describe_volumes",
                fixtures.volumes,
                {"Filters": [{"Name": "tag:Name", "Values": ["test1"]}]},
            )
            for i in bsu.find_volumes_by_tags(self.ec2, "Name:test1"):
                self.assertEqual(i, "vol-a24fffdc")

    def test_find_volumes_by_tags2(self):
        with Stubber(self.ec2) as stubber:
            stubber.add_response(
                "describe_volumes",
                {"Volumes": []},
                {"Filters": [{"Name": "tag:Name", "Values": ["abc"]}]},
            )
            for i in bsu.find_volumes_by_tags(self.ec2, "Name:abc"):
                self.assertEqual(i, None)

    def test_rotate_snapshots1(self):
        with Stubber(self.ec2) as stubber:
            stubber.add_response(
                "describe_snapshots",
                fixtures.snapshots1,
                {
                    "Filters": [
                        {"Name": "volume-id", "Values": ["vol-59b94d63"]},
                        {"Name": "description", "Values": ["osc-bsu-backup 0.0.2"]},
                    ]
                },
            )
            stubber.add_response("delete_snapshot", {}, {"SnapshotId": "snap-d5caf847"})
            stubber.add_response("delete_snapshot", {}, {"SnapshotId": "snap-30e1c236"})
            stubber.add_response("delete_snapshot", {}, {"SnapshotId": "snap-cf4748a5"})

            stubber.add_response(
                "describe_snapshots",
                fixtures.snapshots2,
                {
                    "Filters": [
                        {"Name": "volume-id", "Values": ["vol-640141cf"]},
                        {"Name": "description", "Values": ["osc-bsu-backup 0.0.2"]},
                    ]
                },
            )
            stubber.add_response("delete_snapshot", {}, {"SnapshotId": "snap-9c3c5d34"})
            stubber.add_response("delete_snapshot", {}, {"SnapshotId": "snap-fa25ee50"})
            stubber.add_response("delete_snapshot", {}, {"SnapshotId": "snap-e6996c10"})
            stubber.add_response("delete_snapshot", {}, {"SnapshotId": "snap-8f3436c0"})
            self.assertEqual(
                bsu.rotate_snapshots(self.ec2, ["vol-59b94d63", "vol-640141cf"], 8),
                None,
            )

    def test_rotate_snapshots2(self):
        with Stubber(self.ec2) as stubber:
            stubber.add_response(
                "describe_snapshots",
                fixtures.snapshots1,
                {
                    "Filters": [
                        {"Name": "volume-id", "Values": ["vol-59b94d63"]},
                        {"Name": "description", "Values": ["osc-bsu-backup 0.0.2"]},
                    ]
                },
            )
            stubber.add_response("delete_snapshot", {}, {"SnapshotId": "snap-30e1c236"})
            stubber.add_response("delete_snapshot", {}, {"SnapshotId": "snap-cf4748a5"})
            self.assertEqual(bsu.rotate_snapshots(self.ec2, ["vol-59b94d63"], 9), None)

    def test_rotate_snapshots3(self):
        with Stubber(self.ec2) as stubber:
            stubber.add_response(
                "describe_snapshots",
                fixtures.snapshots1,
                {
                    "Filters": [
                        {"Name": "volume-id", "Values": ["vol-59b94d63"]},
                        {"Name": "description", "Values": ["osc-bsu-backup 0.0.2"]},
                    ]
                },
            )
            self.assertEqual(bsu.rotate_snapshots(self.ec2, ["vol-59b94d63"], 12), None)

    def test_rotate_snapshots4(self):
        with Stubber(self.ec2) as stubber:
            stubber.add_response(
                "describe_snapshots",
                fixtures.snapshots1,
                {
                    "Filters": [
                        {"Name": "volume-id", "Values": ["vol-59b94d63"]},
                        {"Name": "description", "Values": ["osc-bsu-backup 0.0.2"]},
                    ]
                },
            )
            self.assertEqual(
                bsu.rotate_snapshots(self.ec2, ["vol-59b94d63"], -5487812), None
            )

    def test_rotate_snapshots5(self):
        with Stubber(self.ec2) as stubber:
            stubber.add_response(
                "describe_snapshots",
                fixtures.snapshots1,
                {
                    "Filters": [
                        {"Name": "volume-id", "Values": ["vol-59b94d63"]},
                        {"Name": "description", "Values": ["osc-bsu-backup 0.0.2"]},
                    ]
                },
            )
            self.assertEqual(
                bsu.rotate_snapshots(self.ec2, ["vol-59b94d63"], 5487812), None
            )

    def test_rotate_snapshots6(self):
        with Stubber(self.ec2) as stubber:
            stubber.add_response(
                "describe_snapshots",
                {"Snapshots": []},
                {
                    "Filters": [
                        {"Name": "volume-id", "Values": ["aaaa"]},
                        {"Name": "description", "Values": ["osc-bsu-backup 0.0.2"]},
                    ]
                },
            )
            self.assertEqual(bsu.rotate_snapshots(self.ec2, ["aaaa"], 14), None)

    def test_create_snapshots1(self):
        with Stubber(self.ec2) as stubber:
            stubber.add_response(
                "create_snapshot",
                fixtures.create_snapshot1,
                {
                    "Description": "osc-bsu-backup {}".format(__version__),
                    "VolumeId": "vol-56d30e10",
                },
            )
            stubber.add_response(
                "describe_snapshots",
                fixtures.snapshot_completed1,
                {"SnapshotIds": ["snap-91c8d227"]},
            )
            self.assertEqual(bsu.create_snapshots(self.ec2, ["vol-56d30e10"]), None)

    def test_create_snapshots2(self):
        with Stubber(self.ec2) as stubber:
            stubber.add_response(
                "create_snapshot",
                fixtures.create_snapshot1,
                {
                    "Description": "osc-bsu-backup {}".format(__version__),
                    "VolumeId": "vol-56d30e10",
                },
            )
            stubber.add_response(
                "create_snapshot",
                fixtures.create_snapshot2,
                {
                    "Description": "osc-bsu-backup {}".format(__version__),
                    "VolumeId": "vol-640141cf",
                },
            )

            stubber.add_response(
                "describe_snapshots",
                fixtures.snapshot_completed2,
                {"SnapshotIds": ["snap-91c8d227", "snap-f3338f81"]},
            )

            self.assertEqual(
                bsu.create_snapshots(self.ec2, ["vol-56d30e10", "vol-640141cf"]), None
            )


if __name__ == "__main__":
    unittest.main()
