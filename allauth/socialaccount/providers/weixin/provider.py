import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider

from .views import WeixinOAuth2LoginView, WeixinOAuth2CallbackView


class WeixinAccount(ProviderAccount):

    def get_avatar_url(self):
        return self.account.extra_data.get('headimgurl')

    def to_str(self):
        return self.account.extra_data.get('nickname', super(WeixinAccount, self).to_str())


class WeixinProvider(OAuth2Provider):
    id = 'weixin'
    name = 'Weixin'
    account_class = WeixinAccount

    login_view_class = WeixinOAuth2LoginView
    callback_view_class = WeixinOAuth2CallbackView
        
    authorize_url = 'https://open.weixin.qq.com/connect/qrconnect'
    access_token_url = 'https://api.weixin.qq.com/sns/oauth2/access_token'
    profile_url = 'https://api.weixin.qq.com/sns/userinfo'

    def complete_login(self, request, app, token, **kwargs):
        openid = kwargs.get('response', {}).get('openid')
        resp = requests.get(self.get_profile_url(request), params={'access_token': token.token, 'openid': openid})
        extra_data = resp.json()
        nickname = extra_data.get('nickname')
        if nickname:
            extra_data['nickname'] = nickname.encode('raw_unicode_escape').decode('utf-8')
        return self.sociallogin_from_response(request, extra_data)

    def extract_uid(self, data):
        return data['openid']

    def get_default_scope(self):
        return ['snsapi_login']

    def extract_common_fields(self, data):
        return dict(username=data.get('nickname'), name=data.get('nickname'))


provider_classes = [WeixinProvider]
