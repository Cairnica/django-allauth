import re
import requests

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest

from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider

from .views import ShopifyOAuth2LoginView


class ShopifyAccount(ProviderAccount):
    pass


class ShopifyProvider(OAuth2Provider):
    id = 'shopify'
    name = 'Shopify'
    account_class = ShopifyAccount
    
    supports_state = False
    scope_delimiter = ','

    login_view_class = ShopifyOAuth2LoginView

    @property
    def shop_domain(self):
        shop = self.request.GET.get('shop', '')
        if '.' not in shop:
            shop = '{}.myshopify.com'.format(shop)
        # Ensure the provided hostname parameter is a valid hostname,
        # ends with myshopify.com, and does not contain characters
        # other than letters (a-z), numbers (0-9), dots, and hyphens.
        if not re.match(r'^[a-z0-9-]+\.myshopify\.com$', shop):
            raise ImmediateHttpResponse(HttpResponseBadRequest('Invalid `shop` parameter'))
        return shop

    access_token_url = 'https://{shop_domain}/admin/oauth/access_token'
    authorize_url = 'https://{shop_domain}/admin/oauth/authorize'
    profile_url = 'https://{shop_domain}/admin/shop.json'

    def complete_login(self, request, app, token, **kwargs):
        headers = {'X-Shopify-Access-Token': '{token}'.format(token=token.token)}
        response = requests.get(self.get_profile_url(request), headers=headers)
        extra_data = response.json()
        associated_user = kwargs['response'].get('associated_user')
        if associated_user:
            extra_data['associated_user'] = associated_user
        return self.sociallogin_from_response(request, extra_data)

    @property
    def is_per_user(self):
        grant_options = getattr(settings, 'SOCIALACCOUNT_PROVIDERS', {}).get(
            'shopify', {}).get('AUTH_PARAMS', {}).get('grant_options[]', '')
        return grant_options.lower().strip() == 'per-user'

    def get_auth_params(self, request, action):
        ret = super(ShopifyProvider, self).get_auth_params(request, action)
        shop = request.GET.get('shop', None)
        if shop:
            ret.update({'shop': shop})
        return ret

    def get_default_scope(self):
        return ['read_orders', 'read_products']

    def extract_uid(self, data):
        if self.is_per_user:
            return str(data['associated_user']['id'])
        else:
            return str(data['shop']['id'])

    def extract_common_fields(self, data):
        if self.is_per_user:
            return dict(
                email=data['associated_user']['email'],
                first_name=data['associated_user']['first_name'],
                last_name=data['associated_user']['last_name'],
            )
        else:
            # See: https://docs.shopify.com/api/shop
            # Without online mode, User is only available with Shopify Plus,
            # email is the only common field
            return dict(email=data['shop']['email'])


provider_classes = [ShopifyProvider]
