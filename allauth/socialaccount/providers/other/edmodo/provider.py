import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.core.oauth2.provider import OAuth2Provider


class EdmodoAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('profile_url')

    def get_avatar_url(self):
        return self.account.extra_data.get('avatar_url')


class EdmodoProvider(OAuth2Provider):
    id = 'edmodo'
    name = 'Edmodo'
    account_class = EdmodoAccount
    
    access_token_url = 'https://api.edmodo.com/oauth/token'
    authorize_url = 'https://api.edmodo.com/oauth/authorize'
    profile_url = 'https://api.edmodo.com/users/me'

    def get_default_scope(self):
        return ['basic']

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        return dict(first_name=data.get('first_name'),
                    last_name=data.get('last_name'),
                    email=data.get('email', ''))

    def extract_extra_data(self, data):
        return dict(user_type=data.get('type'),
                    profile_url=data.get('url'),
                    avatar_url=data.get('avatars').get('large'))

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.get_profile_url(request), params={'access_token': token.token})
        extra_data = resp.json()
        return self.sociallogin_from_response(request, extra_data)


provider_classes = [EdmodoProvider]
