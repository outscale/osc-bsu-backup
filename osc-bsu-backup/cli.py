import argparse
import logging

logging.basicConfig()
logger = logging.getLogger(__name__).setLevel(logging.INFO)

def main():
    parser = argparse.ArgumentParser(description='osc-ebs-backup')
    parser.add_argument('--instance', dest='instance', action='store', required=True, help='instance to backup')
    parser.add_argument('--rotate', dest='rotate', type=int, action='store', default=10, help='retention for snapshot')
    parser.add_argument('--region', dest='region', action='store', default=False, help='region')
    parser.add_argument('--endpoint', dest='endpoint', action='store', help='endpoint')
    parser.add_argument('--profile', dest='profile', action='store',default="default", help='profile')
    args = parser.parse_args()



if __name__ == '__main__':
    main()
