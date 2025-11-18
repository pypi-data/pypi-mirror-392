#!/usr/bin/python

# Support keystone v3 only
import os
import re
from datetime import datetime, timezone

from keystoneauth1 import loading
from keystoneauth1 import session
from keystoneauth1.exceptions import TokenNotFound
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
        # Track cached clients to invalidate on session refresh
        self._cached_clients = {}

    def get_session(self):
        if self.auth_url is None:
            raise ValueError('Missing auth_url')

        loader = loading.get_plugin_loader('password')
        auth = loader.load_from_options(auth_url=self.auth_url, username = self.username, user_domain_id = self.user_domain_id,
                                        password = self.password, project_id = self.project_id)
        sess = session.Session(auth=auth)
        return sess

    def is_session_expired(self):
        """
        Check if the current session token is expired or about to expire.

        Returns:
            bool: True if session is expired or will expire within 60 seconds, False otherwise
        """
        if self.sess is None:
            return True

        try:
            # Try to get the token - this will raise TokenNotFound if expired
            token = self.sess.get_token()
            if not token:
                return True

            # Check if auth plugin has expiration info
            auth_ref = self.sess.auth
            if hasattr(auth_ref, 'get_access'):
                try:
                    access = auth_ref.get_access(self.sess)
                    if access and hasattr(access, 'auth_ref') and access.auth_ref:
                        expires_at = access.auth_ref.expires
                        if expires_at:
                            # Check if token expires within 60 seconds (buffer time)
                            now = datetime.now(timezone.utc)

                            # Handle different datetime formats
                            # keystoneauth1 typically returns datetime objects, but handle strings too
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
                except (AttributeError, TypeError):
                    # If we can't access expiration info, assume valid
                    pass

            return False
        except (TokenNotFound, AttributeError, Exception):
            # If we can't determine expiration, assume it's expired to be safe
            return True

    def refresh_session(self):
        """
        Refresh the session by creating a new authentication session.
        This will invalidate all cached clients.
        """
        # Clear cached clients since they're tied to the old session
        self._cached_clients.clear()
        # Clear cached service client properties
        for attr in ['_nova', '_keystone', '_cinder', '_neutron', '_allocation', '_glance']:
            if hasattr(self, attr):
                delattr(self, attr)

        # Create a new session
        self.sess = self.get_session()

    def ensure_valid_session(self):
        """
        Ensure the session is valid, refreshing if necessary.
        This is called automatically before operations that require authentication.
        """
        if self.is_session_expired():
            self.refresh_session()

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
        """Get the current authentication token, refreshing if expired."""
        self.ensure_valid_session()
        return self.sess.get_token()

    @property
    def nova(self):
        """Get Nova compute client, ensuring session is valid."""
        self.ensure_valid_session()
        try:
            return self._nova
        except AttributeError:
            self._nova = self.get_nova_client()
            return self._nova

    @property
    def keystone(self):
        """Get Keystone identity client, ensuring session is valid."""
        self.ensure_valid_session()
        try:
            return self._keystone
        except AttributeError:
            self._keystone = self.get_keystone_client()
            return self._keystone

    @property
    def cinder(self):
        """Get Cinder volume client, ensuring session is valid."""
        self.ensure_valid_session()
        try:
            return self._cinder
        except AttributeError:
            self._cinder = self.get_cinder_client()
            return self._cinder

    @property
    def neutron(self):
        """Get Neutron network client, ensuring session is valid."""
        self.ensure_valid_session()
        try:
            return self._neutron
        except AttributeError:
            self._neutron = self.get_neutron_client()
            return self._neutron

    @property
    def allocation(self):
        """Get Allocation client, ensuring session is valid."""
        self.ensure_valid_session()
        try:
            return self._allocation
        except AttributeError:
            self._allocation = self.get_allocation_client()
            return self._allocation

    @property
    def glance(self):
        """Get Glance image client, ensuring session is valid."""
        self.ensure_valid_session()
        try:
            return self._glance
        except AttributeError:
            self._glance = self.get_glance_client()
            return self._glance
