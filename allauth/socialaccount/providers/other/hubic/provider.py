import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.core.oauth2.provider import OAuth2Provider


class HubicAccount(ProviderAccount):
    pass


class HubicProvider(OAuth2Provider):
    id = 'hubic'
    name = 'Hubic'
    account_class = HubicAccount
    
    access_token_url = 'https://api.hubic.com/oauth/token'
    authorize_url = 'https://api.hubic.com/oauth/auth'
    profile_url = 'https://api.hubic.com/1.0/account'
    redirect_uri_protocol = 'https'

    def complete_login(self, request, app, token, **kwargs):
        token_type = kwargs['response']['token_type']
        resp = requests.get(self.get_profile_url(request), headers={'Authorization': '%s %s' % (token_type, token.token)})
        extra_data = resp.json()
        return self.sociallogin_from_response(request, extra_data)

    def extract_uid(self, data):
        return str(data['email'])

    def extract_common_fields(self, data):
        return dict(
            email=data.get('email'),
            username=data.get('firstname').lower() + data.get(
                'lastname').lower(),
            first_name=data.get('firstname'),
            last_name=data.get('lastname'))


provider_classes = [HubicProvider]
