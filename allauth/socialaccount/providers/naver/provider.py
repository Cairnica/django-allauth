import requests

from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class NaverAccount(ProviderAccount):

    def get_avatar_url(self):
        return self.account.extra_data.get('profile_image')

    def to_str(self):
        return self.account.extra_data.get('nickname', self.account.uid)


class NaverProvider(OAuth2Provider):
    id = 'naver'
    name = 'Naver'
    account_class = NaverAccount
    
    access_token_url = 'https://nid.naver.com/oauth2.0/token'
    authorize_url = 'https://nid.naver.com/oauth2.0/authorize'
    profile_url = 'https://openapi.naver.com/v1/nid/me'

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': 'Bearer {0}'.format(token.token)}
        resp = requests.get(self.get_profile_url(request), headers=headers)
        extra_data = resp.json().get('response')
        return self.sociallogin_from_response(request, extra_data)

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        email = data.get("email")
        return dict(email=email)

    def extract_email_addresses(self, data):
        ret = []
        email = data.get("email")
        if email:
            ret.append(EmailAddress(email=email, verified=True, primary=True))
        return ret


provider_classes = [NaverProvider]
