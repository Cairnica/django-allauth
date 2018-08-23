import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.core.oauth2.provider import OAuth2Provider


class BitlyAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('profile_url')

    def get_avatar_url(self):
        return self.account.extra_data.get('profile_image')

    def to_str(self):
        dflt = super(BitlyAccount, self).to_str()
        return '%s (%s)' % (
            self.account.extra_data.get('full_name', ''),
            dflt,
        )


class BitlyProvider(OAuth2Provider):
    id = 'bitly'
    name = 'Bitly'
    account_class = BitlyAccount

    access_token_url = 'https://api-ssl.bitly.com/oauth/access_token'
    authorize_url = 'https://bitly.com/oauth/authorize'
    profile_url = 'https://api-ssl.bitly.com/v3/user/info'
    supports_state = False

    def extract_uid(self, data):
        return str(data['login'])

    def extract_common_fields(self, data):
        return dict(username=data['login'], name=data.get('full_name'))

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(
            self.get_profile_url(request),
            params={'access_token': token.token}
        )
        extra_data = resp.json()['data']
        return self.sociallogin_from_response(request, extra_data)


provider_classes = [BitlyProvider]
