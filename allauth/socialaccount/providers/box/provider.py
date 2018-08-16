import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class BoxOAuth2Account(ProviderAccount):
    pass


class BoxOAuth2Provider(OAuth2Provider):
    id = 'box'
    name = 'Box'
    account_class = BoxOAuth2Account

    access_token_url = 'https://api.box.com/oauth2/token'
    authorize_url = 'https://account.box.com/api/oauth2/authorize'
    profile_url = 'https://api.box.com/2.0/users/me'
    redirect_uri_protocol = None

    def extract_uid(self, data):
        return data['id']

    def extract_common_fields(self, data):
        return dict(name=data.get('display_name'), email=data.get('email'))

    def complete_login(self, request, app, token, **kwargs):
        extra_data = requests.get(self.get_profile_url(request), params={
            'access_token': token.token
        })

        # This only here because of weird response from the test suite
        if isinstance(extra_data, list):
            extra_data = extra_data[0]

        return self.sociallogin_from_response(
            request,
            extra_data.json()
        )


provider_classes = [BoxOAuth2Provider]
