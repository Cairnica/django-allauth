import requests

from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.core.oauth2.provider import OAuth2Provider


class DropboxOAuth2Account(ProviderAccount):
    pass


class DropboxOAuth2Provider(OAuth2Provider):
    id = 'dropbox'
    name = 'Dropbox'
    account_class = DropboxOAuth2Account
    
    access_token_url = 'https://api.dropbox.com/oauth2/token'
    authorize_url = 'https://www.dropbox.com/oauth2/authorize'
    profile_url = 'https://api.dropbox.com/2/users/get_current_account'
    redirect_uri_protocol = 'https'

    def extract_uid(self, data):
        return data['account_id']

    def extract_common_fields(self, data):
        return dict(name=data['name']['display_name'],
                    email=data['email'])

    def complete_login(self, request, app, token, **kwargs):
        extra_data = requests.post(self.get_profile_url(request), headers={
            'Authorization': 'Bearer %s' % (token.token, )
        })

        # This only here because of weird response from the test suite
        if isinstance(extra_data, list):
            extra_data = extra_data[0]

        return self.sociallogin_from_response(
            request,
            extra_data.json()
        )


providers.registry.register(DropboxOAuth2Provider)
