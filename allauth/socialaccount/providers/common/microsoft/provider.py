from __future__ import unicode_literals

import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.core.oauth2.provider import OAuth2Provider


class MicrosoftGraphAccount(ProviderAccount):
    def to_str(self):
        name = self.account.extra_data.get('displayName')
        if name.strip() != '':
            return name
        return super(MicrosoftGraphAccount, self).to_str()


class MicrosoftGraphProvider(OAuth2Provider):
    id = str('microsoft')
    name = 'Microsoft Graph'
    account_class = MicrosoftGraphAccount

    tenant = 'common'

    access_token_url = 'https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token'
    authorize_url = 'https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize'
    profile_url = 'https://graph.microsoft.com/v1.0/me/'

    def get_default_scope(self):
        """
        Doc on scopes available at
        https://developer.microsoft.com/en-us/graph/docs/concepts/permissions_reference
        """
        return ['User.Read']

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        return {
            'email': data.get('mail') or data.get('userPrincipalName'),
            'first_name': data.get('givenName'),
            'last_name': data.get('surname')
        }

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': 'Bearer {0}'.format(token.token)}
        resp = requests.get(self.get_profile_url(request), headers=headers)
        extra_data = resp.json()
        return self.sociallogin_from_response(request, extra_data)


provider_classes = [MicrosoftGraphProvider]
