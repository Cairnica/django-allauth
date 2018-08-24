import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.core.oauth.provider import OAuthProvider


class TumblrAccount(ProviderAccount):
    def get_profile_url_(self):
        return 'http://%s.tumblr.com/' \
            % self.account.extra_data.get('name')

    def to_str(self):
        dflt = super(TumblrAccount, self).to_str()
        name = self.account.extra_data.get('name', dflt)
        return name


class TumblrProvider(OAuthProvider):
    id = 'tumblr'
    name = 'Tumblr'
    account_class = TumblrAccount
    
    request_token_url = 'https://www.tumblr.com/oauth/request_token'
    access_token_url = 'https://www.tumblr.com/oauth/access_token'
    authorize_url = 'https://www.tumblr.com/oauth/authorize'
    profile_url = 'http://api.tumblr.com/v2/user/info'

    def complete_login(self, request, app, access_token, **kwargs):
        resp = requests.get(self.profile_url, auth=self.get_auth_header(app, access_token))
        extra_data = resp.json()['response']['user']
        return self.sociallogin_from_response(request, extra_data)

    def extract_uid(self, data):
        return data['name']

    def extract_common_fields(self, data):
        return dict(first_name=data.get('name'),)


provider_classes = [TumblrProvider]
