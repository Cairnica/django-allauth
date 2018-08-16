import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class DaumAccount(ProviderAccount):

    def get_avatar_url(self):
        return self.account.extra_data.get('bigImagePath')

    def to_str(self):
        return self.account.extra_data.get('nickname', self.account.uid)


class DaumProvider(OAuth2Provider):
    id = 'Daum'
    name = 'Daum'
    account_class = DaumAccount

    access_token_url = 'https://apis.daum.net/oauth2/token'
    authorize_url = 'https://apis.daum.net/oauth2/authorize'
    profile_url = 'https://apis.daum.net/user/v1/show.json'

    def extract_uid(self, data):
        return str(data.get('id'))

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.get_profile_url(request), params={
            'access_token': token.token
        })
        extra_data = resp.json().get('result')
        return self.sociallogin_from_response(
            request,
            extra_data
        )


provider_classes = [DaumProvider]
