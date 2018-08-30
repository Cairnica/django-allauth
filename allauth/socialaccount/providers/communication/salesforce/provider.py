import requests

from allauth.account.models import EmailAddress
from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import AuthAction, ProviderAccount
from allauth.socialaccount.providers.core.oauth2.provider import OAuth2Provider


class SalesforceAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('link')

    def get_avatar_url(self):
        return self.account.extra_data.get('picture')

    def to_str(self):
        dflt = super(SalesforceAccount, self).to_str()
        return self.account.extra_data.get('name', dflt)


class SalesforceProvider(OAuth2Provider):
    id = 'salesforce'
    name = 'Salesforce'
    package = 'allauth.socialaccount.providers.salesforce'
    account_class = SalesforceAccount

    @property
    def base_url(self):
        return self.get_app(self.request).key

    authorize_url = '{base_url}/services/oauth2/authorize'
    access_token_url = '{base_url}/services/oauth2/token'
    profile_url = '{base_url}/services/oauth2/userinfo'

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.get_profile_url(request), params={'oauth_token': token})
        resp.raise_for_status()
        extra_data = resp.json()
        return self.sociallogin_from_response(request, extra_data)

    def get_default_scope(self):
        return ['id', 'openid']

    def get_auth_params(self, request, action):
        ret = super(SalesforceProvider, self).get_auth_params(request, action)
        if action == AuthAction.REAUTHENTICATE:
            ret['approval_prompt'] = 'force'
        return ret

    def extract_uid(self, data):
        return str(data['user_id'])

    def extract_common_fields(self, data):
        return dict(email=data.get('email'),
                    last_name=data.get('family_name'),
                    first_name=data.get('given_name'),
                    username=data.get('preferred_username'))

    def extract_email_addresses(self, data):
        # a salesforce user must have an email, but it might not be verified
        email = EmailAddress(email=data.get('email'),
                             primary=True,
                             verified=data.get('email_verified'))
        return [email]

provider_classes = [SalesforceProvider]
