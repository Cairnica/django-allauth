
import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class AmazonAccount(ProviderAccount):
    def to_str(self):
        return self.account.extra_data.get('name', super(AmazonAccount, self).to_str())


class AmazonProvider(OAuth2Provider):
    id = 'amazon'
    name = 'Amazon'
    account_class = AmazonAccount

    access_token_url = 'https://api.amazon.com/auth/o2/token'
    authorize_url = 'http://www.amazon.com/ap/oa'
    profile_url = 'https://www.amazon.com/ap/user/profile'

    supports_state = False
    redirect_uri_protocol = 'https'

    def get_default_scope(self):
        return ['profile']

    def extract_uid(self, data):
        return str(data['user_id'])

    def extract_common_fields(self, data):
        # Hackish way of splitting the fullname.
        # Asumes no middlenames.
        name = data.get('name', '')
        first_name, last_name = name, ''
        if name and ' ' in name:
            first_name, last_name = name.split(' ', 1)
        return {
            'email': data['email'],
            'last_name': last_name,
            'first_name': first_name,
        }

    def complete_login(self, request, app, token, **kwargs):
        response = requests.get(self.get_profile_url(request), params={'access_token': token})
        extra_data = response.json()
        if 'Profile' in extra_data:
            extra_data = {
                'user_id': extra_data['Profile']['CustomerId'],
                'name': extra_data['Profile']['Name'],
                'email': extra_data['Profile']['PrimaryEmail']
            }
        return self.sociallogin_from_response(request, extra_data)


provider_classes = [AmazonProvider]
