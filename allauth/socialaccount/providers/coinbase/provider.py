import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class CoinbaseAccount(ProviderAccount):
    def get_avatar_url(self):
        return None

    def to_str(self):
        return self.account.extra_data.get(
            'name',
            super(CoinbaseAccount, self).to_str())


class CoinbaseProvider(OAuth2Provider):
    id = 'coinbase'
    name = 'Coinbase'
    account_class = CoinbaseAccount

    authorize_url = 'https://coinbase.com/oauth/authorize'
    access_token_url = 'https://coinbase.com/oauth/token'
    profile_url = 'https://coinbase.com/api/v1/users'

    def get_default_scope(self):
        # See: https://coinbase.com/docs/api/permissions
        return ['user']

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        # See: https://coinbase.com/api/doc/1.0/users/index.html
        return dict(name=data['name'], email=data['email'])

    def complete_login(self, request, app, token, **kwargs):
        response = requests.get(self.get_profile_url(request), params={'access_token': token})
        extra_data = response.json()['users'][0]['user']
        return self.sociallogin_from_response(request, extra_data)


provider_classes = [CoinbaseProvider]
