import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class CernAccount(ProviderAccount):
    def to_str(self):
        dflt = super(CernAccount, self).to_str()
        return self.account.extra_data.get('name', dflt)


class CernProvider(OAuth2Provider):
    id = 'cern'
    name = 'Cern'
    account_class = CernAccount

    access_token_url = 'https://oauth.web.cern.ch/OAuth/Token'
    authorize_url = 'https://oauth.web.cern.ch/OAuth/Authorize'
    profile_url = 'https://oauthresource.web.cern.ch/api/User'
    groups_url = 'https://oauthresource.web.cern.ch/api/Groups'

    supports_state = False
    redirect_uri_protocol = 'https'

    def get_auth_params(self, request, action):
        data = super(CernProvider, self).get_auth_params(request, action)
        data['scope'] = 'read:user'
        return data

    def extract_uid(self, data):
        return str(data.get('id'))

    def extract_common_fields(self, data):
        return dict(
            email=data.get('email'),
            username=data.get('username'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            name=data.get('name')
        )

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': 'Bearer {0}'.format(token.token)}
        user_response = requests.get(self.get_profile_url(request), headers=headers)
        groups_response = requests.get(self.groups_url, headers=headers)
        extra_data = user_response.json()
        extra_data.update(groups_response.json())
        return self.sociallogin_from_response(request, extra_data)


provider_classes = [CernProvider]
