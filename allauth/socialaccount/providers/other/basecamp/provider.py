import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.core.oauth2.provider import OAuth2Provider


class BasecampAccount(ProviderAccount):

    def get_avatar_url(self):
        return None

    def to_str(self):
        dflt = super(BasecampAccount, self).to_str()
        return self.account.extra_data.get('name', dflt)


class BasecampProvider(OAuth2Provider):
    id = 'basecamp'
    name = 'Basecamp'
    account_class = BasecampAccount

    access_token_url = 'https://launchpad.37signals.com/authorization/token?type=web_server'  # noqa
    authorize_url = 'https://launchpad.37signals.com/authorization/new'
    profile_url = 'https://launchpad.37signals.com/authorization.json'

    def get_auth_params(self, request, action):
        data = super(BasecampProvider, self).get_auth_params(request, action)
        data['type'] = 'web_server'
        return data

    def extract_uid(self, data):
        data = data['identity']
        return str(data['id'])

    def extract_common_fields(self, data):
        data = data['identity']
        return dict(
            email=data.get('email_address'),
            username=data.get('email_address'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            name="%s %s" % (data.get('first_name'), data.get('last_name')),
        )

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': 'Bearer {0}'.format(token.token)}
        resp = requests.get(self.get_profile_url(request), headers=headers)
        extra_data = resp.json()
        return self.sociallogin_from_response(request, extra_data)

provider_classes = [BasecampProvider]
