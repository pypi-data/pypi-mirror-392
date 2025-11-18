import os
import argparse
from osclient.openstack2 import OpenStack2

# ======== TESTING =======
def main(args):
    openstack = OpenStack2(auth_url=args.os_auth_url, project_id=args.os_project_id, project_name=args.os_project_name,
                          username=args.os_username, password=args.os_password)
    from pprint import pprint
    pprint(openstack.cached_token)
    # ret = openstack.query('compute', 'servers/d3b16941-b552-456f-9737-12b19c574c5a')
    # assert(ret is not None)
    # pprint(ret)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test Openstack2')

    parser.add_argument('--os-auth-url', default=os.environ.get('OS_AUTH_URL'))
    parser.add_argument('--os-project-name', default=os.environ.get('OS_PROJECT_NAME'))
    parser.add_argument('--os-project-id', default=os.environ.get('OS_PROJECT_ID'))
    parser.add_argument('--os-username', default=os.environ.get('OS_USERNAME'))
    parser.add_argument('--os-password', default=os.environ.get('OS_PASSWORD'))
    parser.add_argument('--os-region-name', default=os.environ.get('OS_REGION_NAME'))

    main(parser.parse_args())