from django.conf import settings

import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.core.oauth2.provider import OAuth2Provider


class FirefoxAccountsAccount(ProviderAccount):
    def to_str(self):
        return self.account.uid


class FirefoxAccountsProvider(OAuth2Provider):
    id = 'fxa'
    name = 'Firefox Accounts'
    account_class = FirefoxAccountsAccount
    
    OAUTH_ENDPOINT = 'https://oauth.accounts.firefox.com/v1'
    PROFILE_ENDPOINT = 'https://oauth.accounts.firefox.com/v1'

    access_token_url = '{OAUTH_ENDPOINT}/token'
    authorize_url = '{OAUTH_ENDPOINT}/authorization'
    profile_url = '{PROFILE_ENDPOINT}/profile'

    def get_default_scope(self):
        return ['profile']

    def extract_uid(self, data):
        return str(data['uid'])

    def extract_common_fields(self, data):
        return dict(email=data.get('email'))

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': 'Bearer {0}'.format(token.token)}
        resp = requests.get(self.get_profile_url(request), headers=headers)
        extra_data = resp.json()
        return self.sociallogin_from_response(request, extra_data)


provider_classes = [FirefoxAccountsProvider]
