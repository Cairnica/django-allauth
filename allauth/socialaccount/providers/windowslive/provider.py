from __future__ import unicode_literals

import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class WindowsLiveAccount(ProviderAccount):

    def to_str(self):
        name = '{0} {1}'.format(self.account.extra_data.get('first_name', ''),
                                self.account.extra_data.get('last_name', ''))
        if name.strip() != '':
            return name
        return super(WindowsLiveAccount, self).to_str()


class WindowsLiveProvider(OAuth2Provider):
    id = str('windowslive')
    name = 'Live'
    account_class = WindowsLiveAccount
    
    access_token_url = 'https://login.live.com/oauth20_token.srf'
    authorize_url = 'https://login.live.com/oauth20_authorize.srf'
    profile_url = 'https://apis.live.net/v5.0/me'

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': 'Bearer {0}'.format(token.token)}
        resp = requests.get(self.get_profile_url(request), headers=headers)

        # example of whats returned (in python format):
        # {'first_name': 'James', 'last_name': 'Smith',
        #  'name': 'James Smith', 'locale': 'en_US', 'gender': None,
        #  'emails': {'personal': None, 'account': 'jsmith@example.com',
        #  'business': None, 'preferred': 'jsmith@example.com'},
        #  'link': 'https://profile.live.com/',
        #  'updated_time': '2014-02-07T00:35:27+0000',
        #  'id': '83605e110af6ff98'}

        resp.raise_for_status()
        extra_data = resp.json()
        return self.sociallogin_from_response(request, extra_data)

    def get_default_scope(self):
        """
        Doc on scopes available at
        http://msdn.microsoft.com/en-us/library/dn631845.aspx
        """
        return ['wl.basic', 'wl.emails']

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        try:
            email = data.get('emails').get('preferred')
        except AttributeError:
            email = None

        return dict(email=email,
                    last_name=data.get('last_name'),
                    first_name=data.get('first_name'))


provider_classes = [WindowsLiveProvider]
