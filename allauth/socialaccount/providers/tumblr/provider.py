import json

from allauth.socialaccount.providers.oauth.client import OAuth
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth.provider import OAuthProvider


class TumblrAccount(ProviderAccount):
    def get_profile_url_(self):
        return 'http://%s.tumblr.com/' \
            % self.account.extra_data.get('name')

    def to_str(self):
        dflt = super(TumblrAccount, self).to_str()
        name = self.account.extra_data.get('name', dflt)
        return name


class TumblrAPI(OAuth):
    url = 'http://api.tumblr.com/v2/user/info'

    def get_user_info(self):
        data = json.loads(self.query(self.url))
        return data['response']['user']


class TumblrProvider(OAuthProvider):
    id = 'tumblr'
    name = 'Tumblr'
    account_class = TumblrAccount
    
    request_token_url = 'https://www.tumblr.com/oauth/request_token'
    access_token_url = 'https://www.tumblr.com/oauth/access_token'
    authorize_url = 'https://www.tumblr.com/oauth/authorize'

    def complete_login(self, request, app, token, response):
        client = TumblrAPI(request, app.client_id, app.secret, self.request_token_url)
        extra_data = client.get_user_info()
        return self.sociallogin_from_response(request, extra_data)

    def extract_uid(self, data):
        return data['name']

    def extract_common_fields(self, data):
        return dict(first_name=data.get('name'),)


provider_classes = [TumblrProvider]
