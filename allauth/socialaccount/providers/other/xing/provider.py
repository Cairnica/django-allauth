import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.core.oauth.provider import OAuthProvider


class XingAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('permalink')

    def get_avatar_url(self):
        return self.account.extra_data.get(
            'photo_urls', {}).get('large')

    def to_str(self):
        dflt = super(XingAccount, self).to_str()
        first_name = self.account.extra_data.get('first_name', '')
        last_name = self.account.extra_data.get('last_name', '')
        name = ' '.join([first_name, last_name]).strip()
        return name or dflt


class XingProvider(OAuthProvider):
    id = 'xing'
    name = 'Xing'
    account_class = XingAccount
    
    request_token_url = 'https://api.xing.com/v1/request_token'
    access_token_url = 'https://api.xing.com/v1/access_token'
    authorize_url = 'https://www.xing.com/v1/authorize'
    profile_url = 'https://api.xing.com/v1/users/me.json'

    def complete_login(self, request, app, token, response):
        resp = requests.get(self.profile_url, self.get_auth_header(app, token))
        extra_data = resp.json()['users'][0]
        return self.sociallogin_from_response(request, extra_data)

    def extract_uid(self, data):
        return data['id']

    def extract_common_fields(self, data):
        return dict(email=data.get('active_email'),
                    username=data.get('page_name'),
                    first_name=data.get('first_name'),
                    last_name=data.get('last_name'))


provider_classes = [XingProvider]
