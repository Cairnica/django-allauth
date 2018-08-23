import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.core.oauth2.provider import OAuth2Provider


class TwentyThreeAndMeAccount(ProviderAccount):
    pass


class TwentyThreeAndMeProvider(OAuth2Provider):
    id = 'twentythreeandme'
    slug = '23andme'
    name = '23andMe'
    account_class = TwentyThreeAndMeAccount
    
    access_token_url = 'https://api.23andme.com/token'
    authorize_url = 'https://api.23andme.com/authorize'
    profile_url = 'https://api.23andme.com/1/user/'

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': 'Bearer {0}'.format(token.token)}
        resp = requests.get(self.get_profile_url(request), headers=headers)
        extra_data = resp.json()
        return self.sociallogin_from_response(request, extra_data)

    def extract_uid(self, data):
        return data['id']

    def get_default_scope(self):
        scope = ['basic']
        return scope

    def extract_common_fields(self, data):
        return dict(
            email=data.get('email'),
        )


provider_classes = [TwentyThreeAndMeProvider]
