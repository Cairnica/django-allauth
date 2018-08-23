import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.core.oauth2.provider import OAuth2Provider


class BaiduAccount(ProviderAccount):
    def get_profile_url(self):
        return "http://www.baidu.com/p/" + self.account.extra_data.get('uname')

    def get_avatar_url(self):
        return (
            'http://tb.himg.baidu.com/sys/portraitn/item/' +
            self.account.extra_data.get('portrait'))

    def to_str(self):
        dflt = super(BaiduAccount, self).to_str()
        return self.account.extra_data.get('uname', dflt)


class BaiduProvider(OAuth2Provider):
    id = 'baidu'
    name = 'Baidu'
    account_class = BaiduAccount

    access_token_url = 'https://openapi.baidu.com/oauth/2.0/token'
    authorize_url = 'https://openapi.baidu.com/oauth/2.0/authorize'
    profile_url = 'https://openapi.baidu.com/rest/2.0/passport/users/getLoggedInUser'  # noqa

    def extract_uid(self, data):
        return data['uid']

    def extract_common_fields(self, data):
        return dict(username=data.get('uid'),
                    name=data.get('uname'))

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.get_profile_url(request), params={'access_token': token.token})
        extra_data = resp.json()
        return self.sociallogin_from_response(request, extra_data)


provider_classes = [BaiduProvider]
