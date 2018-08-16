"""
Provider for Patreon
"""
import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class PatreonAccount(ProviderAccount):
    def get_avatar_url(self):
        return self.account.extra_data.get('attributes').get('thumb_url')


class PatreonProvider(OAuth2Provider):
    id = 'patreon'
    name = 'Patreon'
    account_class = PatreonAccount
    
    access_token_url = 'https://api.patreon.com/oauth2/token'
    authorize_url = 'https://www.patreon.com/oauth2/authorize'
    profile_url = 'https://api.patreon.com/oauth2/api/current_user'

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.get_profile_url(request), headers={'Authorization': 'Bearer ' + token.token})
        extra_data = resp.json().get('data')
        return self.sociallogin_from_response(request, extra_data)

    def get_default_scope(self):
        return ['pledges-to-me', 'users', 'my-campaign']

    def extract_uid(self, data):
        return data.get('id')

    def extract_common_fields(self, data):
        details = data['attributes']
        return {
            'email': details.get('email'),
            'fullname': details.get('full_name'),
            'first_name': details.get('first_name'),
            'last_name': details.get('last_name'),
        }


provider_classes = [PatreonProvider]
