import boto3
from osc_bsu_backup.utils import setup_logging
from osc_bsu_backup.error import InputError

logger = setup_logging(__name__)

class BsuBackup:
    def __init__(self, profile, region, endpoint):
        self.profile = profile
        self.region = region
        default_region = ['us-east-2', 'eu-west-2', 'cn-southeast-1', 'us-west-1']

        if not endpoint and self.region in default_region:
            if region == "cn-southeast-1":
                self.endpoint = "https://fcu.{}.outscale.hk".format(region)
            else:
                self.endpoint = "https://fcu.{}.outscale.com".format(region)
        elif not endpoint and self.region not in default_region:
            raise InputError("You must specify an endpoint when the region is not : {}".format(default_region))
        else:
            self.endpoint = endpoint

        logger.info("region: {}".format(self.region))
        logger.info("endpoint: {}".format(self.endpoint))
        logger.info("profile: {}".format(self.profile))

    def auth(self):
        logger.info("Trying to authenticate")

        session = boto3.Session(profile_name=self.profile)
        self.conn = session.client('ec2',  region_name=self.region, endpoint_url=self.endpoint)

        logger.info(self.conn.describe_key_pairs()['KeyPairs'][0])

    def find_instance_by_id(self, id):
        logger.info("find the instance by id")
        return self.conn.describe_instances(InstanceIds=[id])

    def find_instances_by_tags(self, tags):
        logger.info("find the instance by tags")
        tag_key = tags.split(":")[0]
        tag_value = tags.split(":")[1]

        reservations = self.conn.describe_instances(Filters=[{"Name": "tag:{}".format(tag_key), "Values" : [tag_value]}])

        for reservation in reservations["Reservations"]:
            for instance in reservation["Instances"]:
                logger.info("instance found: %s %s", 
                        instance['InstanceId'], 
                        instance['Tags'])

        return reservations

    def rotate_snapshots(self, rotate=10):
        logger.info("rotate_snapshot")
        logger.info(self.conn.describe_vpc())
