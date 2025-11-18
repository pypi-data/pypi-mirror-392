import os, re, sys
import argparse
import requests


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
        if self.auth_url[-1] != "/": self.auth_url[-1] += "/"
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

    def query(self, service='', params='', obj=None):
        if self.cached_token['token'] is None:
            self.get_token()
        if service == '' or service not in self.cached_token['catalog']:
            sys.exit('Invalid service: {}'.format(service))

        url = self.cached_token['catalog'][service] + '/' + params
        url.replace('//', '/')
        headers = {"X-Auth-Token": self.cached_token['token']}
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print('WARNING: Fail to query: {}'.format(url))
            return None

        return res.json()[obj] if obj is not None else res.json()

    def query_url(self, url='', obj=None):
        if self.cached_token['token'] is None:
            self.get_token()
        url.replace('//', '/')
        headers = {"X-Auth-Token": self.cached_token['token']}
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print('WARNING: Fail to query: {}'.format(url))
            return None

        return res.json()[obj] if obj is not None else res.json()
