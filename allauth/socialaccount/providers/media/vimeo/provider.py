import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.core.oauth.provider import OAuthProvider


class VimeoAccount(ProviderAccount):
    pass


class VimeoProvider(OAuthProvider):
    id = 'vimeo'
    name = 'Vimeo'
    account_class = VimeoAccount

    request_token_url = 'https://vimeo.com/oauth/request_token'
    access_token_url = 'https://vimeo.com/oauth/access_token'
    authorize_url = 'https://vimeo.com/oauth/authorize'
    profile_url = 'http://vimeo.com/api/rest/v2?method=vimeo.people.getInfo'

    def complete_login(self, request, app, token, response):
        resp = requests.get(self.profile_url, self.get_auth_header(app, token))
        extra_data = resp.json()
        return self.sociallogin_from_response(request, extra_data)

    def get_default_scope(self):
        scope = []
        return scope

    def extract_uid(self, data):
        return data['id']

    def extract_common_fields(self, data):
        return dict(name=data.get('display_name'),
                    username=data.get('username'))


provider_classes = [VimeoProvider]
