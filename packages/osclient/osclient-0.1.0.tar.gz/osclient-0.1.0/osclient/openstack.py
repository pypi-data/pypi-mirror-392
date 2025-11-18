#!/usr/bin/python

# Support keystone v3 only
import os
import re

from keystoneauth1 import loading
from keystoneauth1 import session
from novaclient import client as nova_client
from keystoneclient.v3 import client as keystone_client
from cinderclient import client as cinder_client
from neutronclient.v2_0 import client as neutron_client
from nectarallocationclient import client as allocation_client
from glanceclient.v2 import client as glance_client


class OpenStack(object):
    def __init__(self,
                 sess=None,
                 auth_url=None,
                 project_id=None,
                 project_name=None,
                 user_domain_id=None,
                 username=None,
                 password=None,
                 project_domain_id=None):

        self.auth_url = re.sub('\"', '', (auth_url if auth_url else os.environ.get('OS_AUTH_URL')))
        self.project_id = re.sub('\"', '', project_id or os.environ.get('OS_PROJECT_ID') or os.environ.get('OS_TENANT_ID'))
        self.project_name = re.sub('\"', '', project_name or os.environ.get('OS_PROJECT_NAME') or os.environ.get('OS_TENANT_NAME'))
        self.user_domain_id = re.sub('\"', '', (user_domain_id or os.environ.get('OS_USER_DOMAIN_ID', 'default')))
        self.username = re.sub('\"', '', username or os.environ.get('OS_USERNAME'))
        self.password = re.sub('\"', '', password or os.environ.get('OS_PASSWORD'))
        self.project_domain_id = re.sub('\"', '', (project_domain_id or os.environ.get('OS_PROJECT_DOMAIN_ID','default')))

        self.sess = sess or self.get_session()

    def get_session(self):
        if self.auth_url is None:
            raise ValueError('Missing auth_url')

        loader = loading.get_plugin_loader('password')
        auth = loader.load_from_options(auth_url=self.auth_url, username = self.username, user_domain_id = self.user_domain_id,
                                        password = self.password, project_id = self.project_id)
        sess = session.Session(auth=auth)
        return sess

    def get_nova_client(self):
        return nova_client.Client('2.60', session=self.sess)

    def get_keystone_client(self):
        return keystone_client.Client(session=self.sess)

    def get_cinder_client(self):
        return cinder_client.Client('3.50', session=self.sess)

    def get_neutron_client(self):
        return neutron_client.Client(session=self.sess)

    def get_allocation_client(self):
        return allocation_client.Client('1', session=self.sess)

    def get_glance_client(self):
        return glance_client.Client('1', session=self.sess)

    @property
    def token(self):
        return self.sess.get_token()

    @property
    def nova(self):
        try:
            return self._nova
        except AttributeError:
            self._nova = self.get_nova_client()
            return self._nova

    @property
    def keystone(self):
        try:
            return self._keystone
        except AttributeError:
            self._keystone = self.get_keystone_client()
            return self._keystone

    @property
    def cinder(self):
        try:
            return self._cinder
        except AttributeError:
            self._cinder = self.get_cinder_client()
            return self._cinder

    @property
    def neutron(self):
        try:
            return self._neutron
        except AttributeError:
            self._neutron = self.get_neutron_client()
            return self._neutron

    @property
    def allocation(self):
        try:
            return self._allocation
        except AttributeError:
            self._allocation = self.get_allocation_client()
            return self._allocation

    @property
    def glance(self):
        try:
            return self._glance
        except AttributeError:
            self._glance = self.get_glance_client()
            return self._glance
