import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.core.oauth2.provider import OAuth2Provider


class StripeAccount(ProviderAccount):
    def to_str(self):
        default = super(StripeAccount, self).to_str()
        return self.account.extra_data.get('business_name', default)


class StripeProvider(OAuth2Provider):
    id = 'stripe'
    name = 'Stripe'
    account_class = StripeAccount
    
    access_token_url = 'https://connect.stripe.com/oauth/token'
    authorize_url = 'https://connect.stripe.com/oauth/authorize'
    profile_url = 'https://api.stripe.com/v1/accounts/%s'

    def complete_login(self, request, app, token, response, **kwargs):
        headers = {'Authorization': 'Bearer {0}'.format(token.token)}
        resp = requests.get(self.get_profile_url(request) % response.get('stripe_user_id'), headers=headers)
        extra_data = resp.json()
        return self.sociallogin_from_response(request, extra_data)

    def extract_uid(self, data):
        return data['id']

    def extract_common_fields(self, data):
        return dict(name=data.get('display_name'),
                    email=data.get('email'))

    def get_default_scope(self):
        return ['read_only']


provider_classes = [StripeProvider]
