"""Provider for Dwolla"""

import requests

from django.conf import settings
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.core.oauth2.provider import OAuth2Provider


ENVIRONMENTS = {
    'production': {
        'auth_url':  'https://www.dwolla.com/oauth/v2/authenticate',
        'token_url': 'https://www.dwolla.com/oauth/v2/token',
    },
    'sandbox': {
        'auth_url':  'https://uat.dwolla.com/oauth/v2/authenticate',
        'token_url': 'https://uat.dwolla.com/oauth/v2/token',
    }
}

ENV = getattr(settings, 'SOCIALACCOUNT_PROVIDERS', {}).get('dwolla', {}).get('ENVIROMENT', 'production')

AUTH_URL = ENVIRONMENTS[ENV]['auth_url']
TOKEN_URL = ENVIRONMENTS[ENV]['token_url']


class DwollaAccount(ProviderAccount):
    """Dwolla Account"""
    pass


class DwollaProvider(OAuth2Provider):
    id = 'dwolla'
    name = 'Dwolla'
    account_class = DwollaAccount

    scope_delimiter = '|'
    
    access_token_url = TOKEN_URL
    authorize_url = AUTH_URL

    def extract_uid(self, data):
        return str(data.get('id', None))

    def extract_common_fields(self, data):
        return dict(
            name=data.get('name'),
        )

    def complete_login(self, request, app, token, response, **kwargs):
        resp = requests.get(
            response['_links']['account']['href'],
            headers={
                'authorization': 'Bearer %s' % token.token,
                'accept': 'application/vnd.dwolla.v1.hal+json',
            },
        )

        extra_data = resp.json()

        return self.sociallogin_from_response(
            request,
            extra_data
        )


provider_classes = [DwollaProvider]
