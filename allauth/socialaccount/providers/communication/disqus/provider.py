import requests

from allauth.account.models import EmailAddress
from allauth.socialaccount.app_settings import QUERY_EMAIL
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.core.oauth2.provider import OAuth2Provider


class DisqusAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('profileUrl')

    def get_avatar_url(self):
        return self.account.extra_data.get('avatar', {}).get('permalink')

    def to_str(self):
        dflt = super(DisqusAccount, self).to_str()
        return self.account.extra_data.get('name', dflt)


class DisqusProvider(OAuth2Provider):
    id = 'disqus'
    name = 'Disqus'
    account_class = DisqusAccount
    
    access_token_url = 'https://disqus.com/api/oauth/2.0/access_token/'
    authorize_url = 'https://disqus.com/api/oauth/2.0/authorize/'
    profile_url = 'https://disqus.com/api/3.0/users/details.json'
    scope_delimiter = ','

    def get_default_scope(self):
        scope = ['read']
        if QUERY_EMAIL:
            scope += ['email']
        return scope

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        return {
            'username': data.get('username'),
            'email': data.get('email'),
            'name': data.get('name'),
        }

    def extract_email_addresses(self, data):
        ret = []
        email = data.get('email')
        if email:
            ret.append(EmailAddress(email=email, verified=True, primary=True))
        return ret

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.get_profile_url(request), params={
                            'access_token': token.token,
                            'api_key': app.client_id,
                            'api_secret': app.secret})
        resp.raise_for_status()

        extra_data = resp.json().get('response')

        login = self.sociallogin_from_response(request, extra_data)
        return login


provider_classes = [DisqusProvider]
