from __future__ import unicode_literals

import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.core.oauth2.provider import OAuth2Provider
from allauth.socialaccount.providers.core.oauth2.views import OAuth2Adapter


class FeedlyAccount(ProviderAccount):
    def get_avatar_url(self):
        return self.account.extra_data.get('picture')

    def to_str(self):
        name = '{0} {1}'.format(self.account.extra_data.get('givenName', ''),
                                self.account.extra_data.get('familyName', ''))
        if name.strip() != '':
            return name
        return super(FeedlyAccount, self).to_str()


class FeedlyProvider(OAuth2Provider):
    id = str('feedly')
    name = 'Feedly'
    account_class = FeedlyAccount
    
    HOST = 'cloud.feedly.com'
    access_token_url = 'https://{HOST}/v3/auth/token' % host
    authorize_url = 'https://{HOST}/v3/auth/auth' % host
    profile_url = 'https://{HOST}/v3/profile' % host

    def get_default_scope(self):
        return ['https://cloud.feedly.com/subscriptions']

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        return dict(email=data.get('email'),
                    last_name=data.get('familyName'),
                    first_name=data.get('givenName'))

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': 'OAuth {0}'.format(token.token)}
        resp = requests.get(self.get_profile_url(request), headers=headers)
        extra_data = resp.json()
        return self.sociallogin_from_response(request, extra_data)


provider_classes = [FeedlyProvider]
