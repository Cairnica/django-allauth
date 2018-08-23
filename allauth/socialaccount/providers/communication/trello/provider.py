import requests

from django.utils.http import urlencode, urlquote

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.core.oauth.provider import OAuthProvider


class TrelloAccount(ProviderAccount):
    def get_profile_url(self):
        return None

    def get_avatar_url(self):
        return None


class TrelloProvider(OAuthProvider):
    id = 'trello'
    name = 'Trello'
    account_class = TrelloAccount

    request_token_url = 'https://trello.com/1/OAuthGetRequestToken'
    authorize_url = 'https://trello.com/1/OAuthAuthorizeToken'
    access_token_url = 'https://trello.com/1/OAuthGetAccessToken'

    def complete_login(self, request, app, token, response):
        # we need to get the member id and the other information
        # check: https://developers.trello.com/advanced-reference/token
        # https://api.trello.com/1/tokens/91a6408305c1e5ec1b0b306688bc2e2f8fe67abf6a2ecec38c17e5b894fcf866?key=[application_key]&token=[optional_auth_token]
        info_url = '{base}{token}?{query}'.format(
            base='https://api.trello.com/1/tokens/',
            token=urlquote(token),
            query=urlencode({
                'key': app.key,
                'token': response.get('oauth_token')
            })
        )
        resp = requests.get(info_url)
        resp.raise_for_status()
        extra_data = resp.json()
        result = self.sociallogin_from_response(request, extra_data)
        return result

    def get_default_scope(self):
        return ['read']

    def extract_uid(self, data):
        return data['id']

    def get_auth_params(self, request, action):
        data = super(TrelloProvider, self).get_auth_params(request, action)
        app = self.get_app(request)
        data['type'] = 'web_server'
        data['name'] = app.name
        # define here for how long it will be, this can be configured on the
        # social app
        data['expiration'] = 'never'
        return data


provider_classes = [TrelloProvider]
