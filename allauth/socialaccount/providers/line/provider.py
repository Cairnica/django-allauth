import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class LineAccount(ProviderAccount):

    def get_avatar_url(self):
        return self.account.extra_data.get('pictureUrl')

    def to_str(self):
        return self.account.extra_data.get('displayName', self.account.uid)


class LineProvider(OAuth2Provider):
    id = 'line'
    name = 'Line'
    account_class = LineAccount
    
    access_token_url = 'https://api.line.me/v1/oauth/accessToken'
    authorize_url = 'https://access.line.me/dialog/oauth/weblogin'
    profile_url = 'https://api.line.me/v1/profile'

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': 'Bearer {0}'.format(token.token)}
        resp = requests.get(self.get_profile_url(request), headers=headers)
        extra_data = resp.json()
        return self.sociallogin_from_response(request, extra_data)

    def get_default_scope(self):
        return []

    def extract_uid(self, data):
        return str(data['mid'])


provider_classes = [LineProvider]
