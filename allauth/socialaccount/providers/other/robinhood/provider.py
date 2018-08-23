import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.core.oauth2.provider import OAuth2Provider


class RobinhoodAccount(ProviderAccount):
    def get_avatar_url(self):
        return None

    def to_str(self):
        return self.account.extra_data.get(
            'username',
            super(RobinhoodAccount, self).to_str())


class RobinhoodProvider(OAuth2Provider):
    id = 'robinhood'
    name = 'Robinhood'
    account_class = RobinhoodAccount

    authorize_url = 'https://www.robinhood.com/oauth2/authorize/'
    access_token_url = 'https://api.robinhood.com/oauth2/token/'
    profile_url = 'https://api.robinhood.com/user/id/'

    def complete_login(self, request, app, token, **kwargs):
        response = requests.get(
            self.get_profile_url(request),
            headers={'Authorization': 'Bearer %s' % token.token}
        )
        extra_data = response.json()
        return self.sociallogin_from_response(request, extra_data)

    def get_default_scope(self):
        return ['read']

    def extract_uid(self, data):
        return data['id']

    def extract_common_fields(self, data):
        return dict(username=data.get('username'))


provider_classes = [RobinhoodProvider]
