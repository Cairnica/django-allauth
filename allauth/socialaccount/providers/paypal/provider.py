import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class PaypalAccount(ProviderAccount):
    def get_avatar_url(self):
        return self.account.extra_data.get('picture')

    def to_str(self):
        return self.account.extra_data.get('name', super(PaypalAccount, self).to_str())


class PaypalProvider(OAuth2Provider):
    id = 'paypal'
    name = 'Paypal'
    account_class = PaypalAccount

    supports_state = False

    @property
    def authorize_url(self):
        path = 'webapps/auth/protocol/openidconnect/v1/authorize'
        return 'https://www.{0}/{1}'.format(self._get_endpoint(), path)

    @property
    def access_token_url(self):
        path = "v1/identity/openidconnect/tokenservice"
        return 'https://api.{0}/{1}'.format(self._get_endpoint(), path)

    @property
    def profile_url(self):
        path = 'v1/identity/openidconnect/userinfo'
        return 'https://api.{0}/{1}'.format(self._get_endpoint(), path)

    def _get_endpoint(self):
        if self.settings.get('MODE') == 'live':
            return 'paypal.com'
        else:
            return 'sandbox.paypal.com'

    def complete_login(self, request, app, token, **kwargs):
        response = requests.post(
            self.get_profile_url(request),
            params={'schema': 'openid', 'access_token': token}
        )
        extra_data = response.json()
        return self.sociallogin_from_response(request, extra_data)

    def get_default_scope(self):
        # See: https://developer.paypal.com/docs/integration/direct/identity/attributes/  # noqa
        return ['openid', 'email']

    def extract_uid(self, data):
        return str(data['user_id'])

    def extract_common_fields(self, data):
        # See: https://developer.paypal.com/docs/api/#get-user-information
        return dict(first_name=data.get('given_name', ''),
                    last_name=data.get('family_name', ''),
                    email=data.get('email'))


provider_classes = [PaypalProvider]
