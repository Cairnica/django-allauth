import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.core.oauth2.provider import OAuth2Provider


class AgaveAccount(ProviderAccount):

    def get_profile_url(self):
        return self.account.extra_data.get('web_url', 'dflt')

    def get_avatar_url(self):
        return self.account.extra_data.get('avatar_url', 'dflt')

    def to_str(self):
        dflt = super(AgaveAccount, self).to_str()
        return self.account.extra_data.get('name', dflt)


class AgaveProvider(OAuth2Provider):
    id = 'agave'
    name = 'Agave'
    account_class = AgaveAccount

    provider_base_url = 'https://public.agaveapi.co'

    access_token_url = '{provider_base_url}/token'
    authorize_url = '{provider_base_url}/authorize'
    profile_url = '{provider_base_url}/profiles/v2/me'

    def extract_uid(self, data):
        return str(data.get('create_time'))

    def extract_common_fields(self, data):
        return dict(
            email=data.get('email'),
            username=data.get('username'),
            name=(data.get('first_name') + ' ' + data.get('last_name')),
        )

    def get_default_scope(self):
        scope = ['PRODUCTION']
        return scope

    def complete_login(self, request, app, token, response):
        extra_data = requests.get(self.get_profile_url(request), params={
            'access_token': token.token
        }, headers={
            'Authorization': 'Bearer ' + token.token,
        })

        return self.sociallogin_from_response(
            request,
            extra_data.json()['result']
        )


provider_classes = [AgaveProvider]
