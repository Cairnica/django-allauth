from __future__ import unicode_literals

import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class YahooAccount(ProviderAccount):

    def to_str(self):
        name = '{0} {1}'.format(
            self.account.extra_data['profile'].get('givenName', ''),
            self.account.extra_data['profile'].get('familyName', '')
        )
        if name.strip() != '':
            return name
        return super(YahooAccount, self).to_str()


class YahooProvider(OAuth2Provider):
    id = str('yahoo')
    name = 'Yahoo'
    account_class = YahooAccount
    
    access_token_url = 'https://api.login.yahoo.com/oauth2/get_token'
    authorize_url = 'https://api.login.yahoo.com/oauth2/request_auth'
    profile_url = 'https://social.yahooapis.com/v1/user/me/profile?format=json'

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': 'Bearer {0}'.format(token.token)}
        resp = requests.get(self.get_profile_url(request), headers=headers)

        extra_data = resp.json()
        return self.sociallogin_from_response(request, extra_data)

    def get_default_scope(self):
        """
        Doc on scopes available at
        https://developer.yahoo.com/oauth2/guide/yahoo_scopes/
        """
        return ['sdps-r']

    def extract_uid(self, data):
        return str(data['profile']['guid'])

    def extract_common_fields(self, data):
        emails = data['profile'].get('emails')
        if emails:
            email = emails[0]['handle']
        else:
            email = None

        return dict(email=email,
                    last_name=data['profile'].get('familyName'),
                    first_name=data['profile'].get('givenName'))


provider_classes = [YahooProvider]
