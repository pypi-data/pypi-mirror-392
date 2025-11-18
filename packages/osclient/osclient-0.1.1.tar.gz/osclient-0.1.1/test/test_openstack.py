import os
import argparse
from osclient.openstack import OpenStack

# ======== TESTING =======
def main(args):
    openstack = OpenStack(auth_url=args.os_auth_url, project_id=args.os_project_id, project_name=args.os_project_name,
                          username=args.os_username, password=args.os_password)
    from pprint import pprint
    pprint(openstack.token)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test Openstack2')

    parser.add_argument('--os-auth-url', default=os.environ.get('OS_AUTH_URL'))
    parser.add_argument('--os-project-name', default=os.environ.get('OS_PROJECT_NAME'))
    parser.add_argument('--os-project-id', default=os.environ.get('OS_PROJECT_ID'))
    parser.add_argument('--os-username', default=os.environ.get('OS_USERNAME'))
    parser.add_argument('--os-password', default=os.environ.get('OS_PASSWORD'))
    parser.add_argument('--os-region-name', default=os.environ.get('OS_REGION_NAME'))

    main(parser.parse_args())
