import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.core.oauth2.provider import OAuth2Provider


class DigitalOceanAccount(ProviderAccount):
    pass


class DigitalOceanProvider(OAuth2Provider):
    id = 'digitalocean'
    name = 'DigitalOcean'
    account_class = DigitalOceanAccount
    
    access_token_url = 'https://cloud.digitalocean.com/v1/oauth/token'
    authorize_url = 'https://cloud.digitalocean.com/v1/oauth/authorize'
    profile_url = 'https://api.digitalocean.com/v2/account'

    def extract_uid(self, data):
        return str(data['account']['uuid'])

    def extract_common_fields(self, data):
        return dict(email=data['account']['email'])

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': 'Bearer {0}'.format(token.token)}
        resp = requests.get(self.get_profile_url(request), headers=headers)
        extra_data = resp.json()
        return self.sociallogin_from_response(
            request, extra_data)


provider_classes = [DigitalOceanProvider]
