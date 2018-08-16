import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class StackExchangeAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('html_url')

    def get_avatar_url(self):
        return self.account.extra_data.get('avatar_url')

    def to_str(self):
        dflt = super(StackExchangeAccount, self).to_str()
        return self.account.extra_data.get('name', dflt)


class StackExchangeProvider(OAuth2Provider):
    id = 'stackexchange'
    name = 'Stack Exchange'
    account_class = StackExchangeAccount
    
    access_token_url = 'https://stackexchange.com/oauth/access_token'
    authorize_url = 'https://stackexchange.com/oauth'
    profile_url = 'https://api.stackexchange.com/2.1/me'

    def complete_login(self, request, app, token, **kwargs):
        site = self.get_site()
        resp = requests.get(self.get_profile_url(request), params={'access_token': token.token, 'key': app.key, 'site': site})
        extra_data = resp.json()['items'][0]
        return self.sociallogin_from_response(request, extra_data)

    def get_site(self):
        settings = self.get_settings()
        return settings.get('SITE', 'stackoverflow')

    def extract_uid(self, data):
        # `user_id` varies if you use the same account for
        # e.g. StackOverflow and ServerFault. Therefore, we pick
        # `account_id`.
        uid = str(data['account_id'])
        return uid

    def extract_common_fields(self, data):
        return dict(username=data.get('display_name'))


provider_classes = [StackExchangeProvider]
