import json

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.core.oauth.provider import OAuthProvider
from allauth.socialaccount.providers.core.oauth.client import OAuth


class BitbucketAPI(OAuth):

    emails_url = 'https://bitbucket.org/api/1.0/emails/'
    users_url = 'https://bitbucket.org/api/1.0/users/'

    def get_user_info(self):
        # TODO: Actually turn these into EmailAddress
        emails = json.loads(self.query(self.emails_url))
        for address in reversed(emails):
            if address['active']:
                email = address['email']
                if address['primary']:
                    break
        data = json.loads(self.query(self.users_url + email))
        user = data['user']
        return user


class BitbucketAccount(ProviderAccount):
    def get_profile_url(self):
        return 'http://bitbucket.org/' + self.account.extra_data['username']

    def get_avatar_url(self):
        return self.account.extra_data.get('avatar')

    def get_username(self):
        return self.account.extra_data['username']

    def to_str(self):
        return self.get_username()


class BitbucketProvider(OAuthProvider):
    id = 'bitbucket'
    name = 'Bitbucket'
    account_class = BitbucketAccount

    request_token_url = 'https://bitbucket.org/api/1.0/oauth/request_token'
    access_token_url = 'https://bitbucket.org/api/1.0/oauth/access_token'
    authorize_url = 'https://bitbucket.org/api/1.0/oauth/authenticate'

    def extract_uid(self, data):
        return data['username']

    def extract_common_fields(self, data):
        return dict(email=data.get('email'),
                    first_name=data.get('first_name'),
                    username=data.get('username'),
                    last_name=data.get('last_name'))

    def complete_login(self, request, app, token, response):
        client = BitbucketAPI(request, app.client_id, app.secret, self.request_token_url)
        extra_data = client.get_user_info()
        return self.sociallogin_from_response(request, extra_data)


provider_classes = [BitbucketProvider]
