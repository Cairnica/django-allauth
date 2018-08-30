import requests

from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.core.oauth2.provider import OAuth2Provider


class GlobusAccount(ProviderAccount):

    def get_profile_url(self):
        return self.account.extra_data.get('web_url', 'dflt')

    def get_avatar_url(self):
        return self.account.extra_data.get('avatar_url', 'dflt')

    def to_str(self):
        dflt = super(GlobusAccount, self).to_str()
        return self.account.extra_data.get('name', dflt)


class GlobusProvider(OAuth2Provider):
    id = 'globus'
    name = 'Globus'
    account_class = GlobusAccount
    
    provider_base_url = 'https://auth.globus.org/v2/oauth2'
    
    access_token_url = '{provider_base_url}/token'
    authorize_url = '{provider_base_url}/authorize'
    profile_url = '{provider_base_url}/userinfo'

    def extract_uid(self, data):
        return str(data.get('create_time'))

    def extract_common_fields(self, data):
        return dict(
            email=data.get('email'),
            username=data.get('preferred_username'),
            name=data.get('name'),
        )

    def get_default_scope(self):
        scope = ['openid', 'profile', 'offline_access']
        if app_settings.QUERY_EMAIL:
            scope.append('email')
        return scope

    def complete_login(self, request, app, token, response):
        extra_data = requests.get(self.get_profile_url(request), params={
            'access_token': token.token
        }, headers={
            'Authorization': 'Bearer ' + token.token,
        })

        return self.sociallogin_from_response(
            request,
            extra_data.json()
        )


provider_classes = [GlobusProvider]
