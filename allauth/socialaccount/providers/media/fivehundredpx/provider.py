import json

from allauth.socialaccount.providers.core.oauth.client import OAuth
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.core.oauth.provider import OAuthProvider


class FiveHundredPxAccount(ProviderAccount):
    def get_profile_url(self):
        return 'https://500px.com/%s' \
            % self.account.extra_data.get('username')

    def get_avatar_url(self):
        return self.account.extra_data.get('userpic_url')

    def to_str(self):
        dflt = super(FiveHundredPxAccount, self).to_str()
        name = self.account.extra_data.get('fullname', dflt)
        return name


API_BASE = 'https://api.500px.com/v1'


class FiveHundredPxAPI(OAuth):
    """
    Verifying 500px credentials
    """
    url = API_BASE + '/users'

    def get_user_info(self):
        return json.loads(self.query(self.url))['user']


class FiveHundredPxProvider(OAuthProvider):
    id = '500px'
    name = '500px'
    account_class = FiveHundredPxAccount
    
    request_token_url = API_BASE + '/oauth/request_token'
    access_token_url = API_BASE + '/oauth/access_token'
    authorize_url = API_BASE + '/oauth/authorize'

    def get_default_scope(self):
        return []

    def extract_uid(self, data):
        return data['id']

    def extract_common_fields(self, data):
        return dict(username=data.get('username'),
                    email=data.get('email'),
                    first_name=data.get('firstname'),
                    last_name=data.get('lastname'))

    def complete_login(self, request, app, token, response):
        client = FiveHundredPxAPI(request, app.client_id, app.secret, self.request_token_url)
        extra_data = client.get_user_info()
        return self.sociallogin_from_response(request, extra_data)


provider_classes = [FiveHundredPxProvider]
