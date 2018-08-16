from __future__ import unicode_literals

import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter

from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter


class MicrosoftGraphOAuth2Adapter(OAuth2Adapter):
    def __init__(self, request):
        super(MicrosoftGraphOAuth2Adapter, self).__init__(request)
        provider = self.get_provider()
        tenant = provider.get_settings().get('tenant') or 'common'
        base_url = 'https://login.microsoftonline.com/{0}'.format(tenant)
        self.access_token_url = '{0}/oauth2/v2.0/token'.format(base_url)
        self.authorize_url = '{0}/oauth2/v2.0/authorize'.format(base_url)
        self.profile_url = 'https://graph.microsoft.com/v1.0/me/'

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': 'Bearer {0}'.format(token.token)}
        resp = requests.get(self.profile_url, headers=headers)
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


class MicrosoftGraphAccount(ProviderAccount):

    def to_str(self):
        name = self.account.extra_data.get('displayName')
        if name.strip() != '':
            return name
        return super(MicrosoftGraphAccount, self).to_str()


class MicrosoftGraphProvider(OAuth2Provider):
    id = str('microsoft')
    name = 'Microsoft Graph'
    adapter_class = MicrosoftGraphOAuth2Adapter
    account_class = MicrosoftGraphAccount

    def get_default_scope(self):
        """
        Doc on scopes available at
        https://developer.microsoft.com/en-us/graph/docs/concepts/permissions_reference
        """
        return ['User.Read']

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        email = data.get('mail') or data.get('userPrincipalName')
        return dict(email=email,
                    last_name=data.get('surname'),
                    first_name=data.get('givenName'))


provider_classes = [MicrosoftGraphProvider]
