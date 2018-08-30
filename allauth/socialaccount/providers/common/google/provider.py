import requests

from allauth.account.models import EmailAddress
from allauth.socialaccount.app_settings import QUERY_EMAIL
from allauth.socialaccount.providers.base import AuthAction, ProviderAccount
from allauth.socialaccount.providers.core.oauth2.provider import OAuth2Provider


class Scope(object):
    EMAIL = 'email'
    PROFILE = 'profile'


class GoogleAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('link')

    def get_avatar_url(self):
        return self.account.extra_data.get('picture')

    def to_str(self):
        dflt = super(GoogleAccount, self).to_str()
        return self.account.extra_data.get('name', dflt)


class GoogleProvider(OAuth2Provider):
    id = 'google'
    name = 'Google'
    account_class = GoogleAccount
    
    access_token_url = 'https://accounts.google.com/o/oauth2/token'
    authorize_url = 'https://accounts.google.com/o/oauth2/auth'
    profile_url = 'https://www.googleapis.com/oauth2/v1/userinfo'

    def get_default_scope(self):
        scope = [Scope.PROFILE]
        if QUERY_EMAIL:
            scope.append(Scope.EMAIL)
        return scope

    def get_auth_params(self, request, action):
        ret = super(GoogleProvider, self).get_auth_params(request,
                                                          action)
        if action == AuthAction.REAUTHENTICATE:
            ret['prompt'] = 'select_account consent'
        return ret

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        return dict(email=data.get('email'),
                    last_name=data.get('family_name'),
                    first_name=data.get('given_name'))

    def extract_email_addresses(self, data):
        ret = []
        email = data.get('email')
        if email and data.get('verified_email'):
            ret.append(EmailAddress(email=email,
                       verified=True,
                       primary=True))
        return ret

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.get_profile_url(request), params={'access_token': token.token, 'alt': 'json'})
        resp.raise_for_status()
        extra_data = resp.json()
        login = self.sociallogin_from_response(request, extra_data)
        return login


provider_classes = [GoogleProvider]
