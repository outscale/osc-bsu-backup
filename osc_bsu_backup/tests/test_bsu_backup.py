import unittest
import logging
from unittest.mock import patch
import botocore

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

    def test_auth(self):
        bsu_ = bsu.BsuBackup(region="eu-west-2", profile="azrzrgzefv", endpoint=None)
        self.assertRaises(botocore.exceptions.ProfileNotFound, bsu_.auth)


if __name__ == "__main__":
    unittest.main()
