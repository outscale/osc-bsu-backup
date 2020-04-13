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


class TestBsuBackup(unittest.TestCase):
    def setUp(self):
        #logging.disable(logging.CRITICAL)
        return

    def tearDown(self):
        #logging.disable(logging.NOTSET)
        return

    def test_auth(self):
        with patch('boto3.Session'):
            self.assertTrue(bsu.auth(region="eu-west-2", profile="default", endpoint=None))
        self.assertRaises(InputError, bsu.auth, "eu-west-3", "default", None)

    def test_find_instance_by_id(self):
        ec2 = botocore.session.get_session().create_client('ec2')
        stubber = Stubber(ec2)

        with open(os.getcwd()+'/osc_bsu_backup/tests/fixtures/describe_instances.json') as handle:
            response = json.loads(handle.read())

        with Stubber(ec2) as stubber:
            stubber.add_response('describe_instances', response, {'InstanceIds': ['i-e6b7ab04']})
            self.assertEqual(bsu.find_instance_by_id(ec2, "i-e6b7ab04"), response)

        with Stubber(ec2) as stubber:
            stubber.add_response('describe_instances', {}, {'InstanceIds': ['i-e6b7ab05']})
            self.assertNotEqual(bsu.find_instance_by_id(ec2, "i-e6b7ab05"), response)

    def test_find_instance_by_tags(self):
        ec2 = botocore.session.get_session().create_client('ec2')
        stubber = Stubber(ec2)

        with open(os.getcwd()+'/osc_bsu_backup/tests/fixtures/describe_instances.json') as handle:
            response = json.loads(handle.read())

        with Stubber(ec2) as stubber:
            stubber.add_response('describe_instances', response, { 'Filters' : [{"Name": "tag:Name", "Values": ["test1"]}]} )

            self.assertIs(bsu.find_instances_by_tags(ec2, "Name:test1"), response)


if __name__ == "__main__":
    unittest.main()
