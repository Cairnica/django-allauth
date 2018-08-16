import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter


class AgaveAccount(ProviderAccount):

    def get_profile_url(self):
        return self.account.extra_data.get('web_url', 'dflt')

    def get_avatar_url(self):
        return self.account.extra_data.get('avatar_url', 'dflt')

    def to_str(self):
        dflt = super(AgaveAccount, self).to_str()
        return self.account.extra_data.get('name', dflt)


class AgaveAdapter(OAuth2Adapter):
    provider_default_url = 'https://public.agaveapi.co/'
    provider_api_version = 'v2'

    provider_base_url = 'https://public.agaveapi.co'

    access_token_url = '{0}/token'.format(provider_base_url)
    authorize_url = '{0}/authorize'.format(provider_base_url)
    profile_url = '{0}/profiles/v2/me'.format(provider_base_url)

    def complete_login(self, request, app, token, response):
        extra_data = requests.get(self.profile_url, params={
            'access_token': token.token
        }, headers={
            'Authorization': 'Bearer ' + token.token,
        })

        return self.get_provider().sociallogin_from_response(
            request,
            extra_data.json()['result']
        )


class AgaveProvider(OAuth2Provider):
    id = 'agave'
    name = 'Agave'
    adapter_class = AgaveAdapter
    account_class = AgaveAccount

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


provider_classes = [AgaveProvider]
