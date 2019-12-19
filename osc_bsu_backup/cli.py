import argparse
import logging
from osc_bsu_backup.bsu_backup import BsuBackup
from osc_bsu_backup.utils import setup_logging

logger = setup_logging(__name__)

def main():
    logger.info("osc_bsu_backup")

    parser = argparse.ArgumentParser(description='osc-ebs-backup')
    parser.add_argument('--instance-by-id', dest='instance_id', action='store', 
            help='instance to backup')
    parser.add_argument('--instance-by-tags', dest='instance_tags', action='store', 
            help='instances tags to look for use the format Key:Value')
    parser.add_argument('--rotate', dest='rotate', type=int, action='store', default=10, 
            help='retention for snapshot')
    parser.add_argument('--region', dest='region', action='store', default="eu-west-2", 
            help='region')
    parser.add_argument('--endpoint', dest='endpoint', default=None, action='store', 
            help='endpoint')
    parser.add_argument('--profile', dest='profile', action='store',default="default", 
            help='profile')
    args = parser.parse_args()

    back = BsuBackup(args.profile, args.region, args.endpoint)

    back.auth()
    

    if args.instance_id:
        back.find_instance_by_id(args.instance_id)
    elif args.instance_tags:
        if len(args.instance_tags.split(":")) != 2:
            parser.error('please use the format Key:Value for tags: --instance-by-tags Name:vm-1')
        back.find_instances_by_tags(args.instance_tags)
    else:
        parser.error('please use --instance-by-id or --instance-by-tags')

if __name__ == '__main__':
    main()
