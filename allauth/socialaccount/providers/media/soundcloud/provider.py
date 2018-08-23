import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.core.oauth2.provider import OAuth2Provider


class SoundCloudAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('permalink_url')

    def get_avatar_url(self):
        return self.account.extra_data.get('avatar_url')

    def to_str(self):
        dflt = super(SoundCloudAccount, self).to_str()
        full_name = self.account.extra_data.get('full_name')
        username = self.account.extra_data.get('username')
        return full_name or username or dflt


class SoundCloudProvider(OAuth2Provider):
    id = 'soundcloud'
    name = 'SoundCloud'
    account_class = SoundCloudAccount
    
    access_token_url = 'https://api.soundcloud.com/oauth2/token'
    authorize_url = 'https://soundcloud.com/connect'
    profile_url = 'https://api.soundcloud.com/me.json'

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.get_profile_url(request),
                            params={'oauth_token': token.token})
        extra_data = resp.json()
        return self.sociallogin_from_response(request, extra_data)

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        return dict(name=data.get('full_name'),
                    username=data.get('username'),
                    email=data.get('email'))


provider_classes = [SoundCloudProvider]
