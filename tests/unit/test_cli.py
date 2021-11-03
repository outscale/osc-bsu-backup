import unittest
import logging

from unittest.mock import patch
import osc_bsu_backup.cli as cli
import sys
import botocore


class TestCliMethods(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    @patch("sys.argv", [sys.argv[0]])
    def test_cli(self):
        self.assertRaises(SystemExit, cli.main)

    @patch("sys.argv", [sys.argv[0], "--region", "eu-west-2"])
    def test_cli2(self):
        self.assertRaises(SystemExit, cli.main)

    @patch(
        "sys.argv",
        [sys.argv[0], "--instance-by-id", "i-aaaa", "--profile", "azzqfscxwdqdsf"],
    )
    def test_cli3(self):
        self.assertRaises(botocore.exceptions.ProfileNotFound, cli.main)

    @patch(
        "sys.argv",
        [
            sys.argv[0],
            "--instance-by-tags",
            "Name:test",
            "--instance-by-tags",
            "Nam1:test1",
        ],
    )
    def test_cli4(self):
        self.assertTrue(cli.main)


if __name__ == "__main__":
    unittest.main()
