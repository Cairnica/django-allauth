import json

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.core.oauth.provider import OAuthProvider


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

    emails_url = 'https://bitbucket.org/api/1.0/emails/'
    users_url = 'https://bitbucket.org/api/1.0/users/'

    def extract_uid(self, data):
        return data['username']

    def extract_common_fields(self, data):
        return dict(email=data.get('email'),
                    first_name=data.get('first_name'),
                    username=data.get('username'),
                    last_name=data.get('last_name'))

    def complete_login(self, request, app, token, response):
        auth = self.get_auth_header(app, token)

        emails_resp = requests.get(self.emails_url, auth=auth)
        for address in reversed(emails_resp.json()):
            if address['active']:
                email = address['email']
                if address['primary']:
                    break

        users_resp = requests.get(self.users_url + email, auth=auth)
        extra_data = users_resp.json()['user']
        return self.sociallogin_from_response(request, extra_data)


provider_classes = [BitbucketProvider]
