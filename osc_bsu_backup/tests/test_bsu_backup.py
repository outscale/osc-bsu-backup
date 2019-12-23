import unittest
import logging
from unittest.mock import patch
import boto3

import osc_bsu_backup.bsu_backup as bsu
from osc_bsu_backup.error import InputError


class TestBsuBackupMethods(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_init(self):
        self.assertIsInstance(
            bsu.BsuBackup(region="eu-west-2", profile="default", endpoint=None),
            bsu.BsuBackup,
        )
        self.assertRaises(InputError, bsu.BsuBackup, "eu-west-3", "default", None)
        self.assertEqual(
            bsu.BsuBackup(
                region="eu-west-2", profile="default", endpoint=None
            ).endpoint,
            "https://fcu.eu-west-2.outscale.com",
        )
        self.assertEqual(
            bsu.BsuBackup(
                region="cn-southeast-1", profile="default", endpoint=None
            ).endpoint,
            "https://fcu.cn-southeast-1.outscale.hk",
        )

    @patch("osc_bsu_backup.bsu_backup.boto3")
    def test_auth(self, boto3):
        bsu_ = bsu.BsuBackup(region="eu-west-2", profile="azrzrgzefv", endpoint=None)
        bsu_.auth()
        self.assertIsInstance(bsu_.conn, object)


if __name__ == "__main__":
    unittest.main()
