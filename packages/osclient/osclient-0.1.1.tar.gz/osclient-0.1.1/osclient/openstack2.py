import os, re, sys
import requests
from datetime import datetime, timezone


class OpenStack2(object):
    def __init__(self,
                 auth_url=None,
                 project_id=None,
                 project_name=None,
                 user_domain_id=None,
                 username=None,
                 password=None,
                 project_domain_id=None):

        self.auth_url = re.sub('\"', '', (auth_url if auth_url else os.environ.get('OS_AUTH_URL')))
        # Ensure auth_url ends with a slash
        if self.auth_url and self.auth_url[-1] != "/":
            self.auth_url += "/"
        self.project_id = re.sub('\"', '', project_id or os.environ.get('OS_PROJECT_ID') or os.environ.get('OS_TENANT_ID'))
        self.project_name = re.sub('\"', '', project_name or os.environ.get('OS_PROJECT_NAME') or os.environ.get('OS_TENANT_NAME'))
        self.user_domain_id = re.sub('\"', '', (user_domain_id or os.environ.get('OS_USER_DOMAIN_ID', 'default')))
        self.username = re.sub('\"', '', username or os.environ.get('OS_USERNAME'))
        self.password = re.sub('\"', '', password or os.environ.get('OS_PASSWORD'))
        self.project_domain_id = re.sub('\"', '', (project_domain_id or os.environ.get('OS_PROJECT_DOMAIN_ID','default')))
        # get token and save
        self.cached_token = {'token': None, 'catalog': None, 'issued_at': None, 'expires_at': None}
        self.get_token()

    def _parse_catalog(self, catalog):
        m = {}
        for c in catalog:
            type = c['type']
            for e in c['endpoints']:
                if e['interface'] == 'public':
                    url = e['url']
                    break
            m[type] = url
        return m

    def get_token(self):
        uri = self.auth_url + 'auth/tokens'
        req_body = { "auth": {
                        "identity": {
                            "methods": ["password"],
                            "password": {
                                "user": {
                                    "domain": { "name": self.user_domain_id },
                                    "name": self.username,
                                    "password": self.password
                                }
                            }
                        },
                        "scope": {
                            "project": {
                                "domain": { "name": self.project_domain_id },
                                "name":  self.project_name
                            }
                        }
                    }
                }

        res = requests.post(uri, json=req_body)
        if res.status_code != 201:
            sys.exit('Openstack.authenticate: could not authenticate as admin!')

        self.cached_token['token'] = res.headers._store['x-subject-token'][1]
        self.cached_token['catalog'] = self._parse_catalog(res.json()['token']['catalog'])
        self.cached_token['issued_at'] = res.json()['token']['issued_at']
        self.cached_token['expires_at'] = res.json()['token']['expires_at']

    def is_token_expired(self):
        """
        Check if the current token is expired or about to expire.

        Returns:
            bool: True if token is expired or will expire within 60 seconds, False otherwise
        """
        if not self.cached_token.get('token'):
            return True

        expires_at = self.cached_token.get('expires_at')
        if not expires_at:
            # If we don't have expiration info, assume it's valid
            return False

        try:
            # Parse expiration time
            now = datetime.now(timezone.utc)

            # Handle different datetime formats
            if isinstance(expires_at, str):
                # Parse ISO format datetime string
                try:
                    # Try fromisoformat (Python 3.7+)
                    if hasattr(datetime, 'fromisoformat'):
                        expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                    else:
                        # Python 3.6 fallback: parse basic ISO format
                        # Remove microseconds and timezone for strptime
                        dt_str = expires_at.split('.')[0].replace('Z', '')
                        expires_at = datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%S')
                except (AttributeError, ValueError):
                    # If parsing fails, can't determine expiration
                    return False
            elif not isinstance(expires_at, datetime):
                # If it's not a datetime object, can't determine expiration
                return False

            # Ensure timezone-aware datetime
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)

            # Add 60 second buffer to refresh before actual expiration
            buffer_time = 60
            time_until_expiry = (expires_at - now).total_seconds()
            return time_until_expiry <= buffer_time
        except (AttributeError, TypeError, ValueError):
            # If we can't determine expiration, assume it's valid
            return False

    def ensure_valid_token(self):
        """
        Ensure the token is valid, refreshing if necessary.
        This is called automatically before operations that require authentication.
        """
        if self.is_token_expired():
            self.get_token()

    def query(self, service='', params='', obj=None):
        """Query an OpenStack service endpoint, ensuring token is valid."""
        # Ensure token is valid before querying
        self.ensure_valid_token()

        if service == '' or service not in self.cached_token['catalog']:
            sys.exit('Invalid service: {}'.format(service))

        url = self.cached_token['catalog'][service] + '/' + params
        url = url.replace('//', '/')
        headers = {"X-Auth-Token": self.cached_token['token']}
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print('WARNING: Fail to query: {}'.format(url))
            return None

        return res.json()[obj] if obj is not None else res.json()

    def query_url(self, url='', obj=None):
        """Query a direct URL, ensuring token is valid."""
        # Ensure token is valid before querying
        self.ensure_valid_token()

        url = url.replace('//', '/')
        headers = {"X-Auth-Token": self.cached_token['token']}
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print('WARNING: Fail to query: {}'.format(url))
            return None

        return res.json()[obj] if obj is not None else res.json()
