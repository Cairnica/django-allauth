import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.core.oauth2.provider import OAuth2Provider


class AsanaAccount(ProviderAccount):
    pass


class AsanaProvider(OAuth2Provider):
    id = 'asana'
    name = 'Asana'
    account_class = AsanaAccount

    access_token_url = 'https://app.asana.com/-/oauth_token'
    authorize_url = 'https://app.asana.com/-/oauth_authorize'
    profile_url = 'https://app.asana.com/api/1.0/users/me'

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        return {
            'email': data.get('email'),
            'name': data.get('name')
        }

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.get_profile_url(request), params={'access_token': token.token})
        extra_data = resp.json()['data']
        return self.sociallogin_from_response(request, extra_data)


provider_classes = [AsanaProvider]
