import requests

from allauth.socialaccount.providers.base import (
    ProviderAccount,
    ProviderException,
)
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class WeiboAccount(ProviderAccount):
    def get_profile_url(self):
        # profile_url = "u/3195025850"
        return 'http://www.weibo.com/' + self.account.extra_data.get('profile_url')

    def get_avatar_url(self):
        return self.account.extra_data.get('avatar_large')

    def to_str(self):
        dflt = super(WeiboAccount, self).to_str()
        return self.account.extra_data.get('name', dflt)


class WeiboProvider(OAuth2Provider):
    id = 'weibo'
    name = 'Weibo'
    account_class = WeiboAccount
    
    access_token_url = 'https://api.weibo.com/oauth2/access_token'
    authorize_url = 'https://api.weibo.com/oauth2/authorize'
    profile_url = 'https://api.weibo.com/2/users/show.json'

    def complete_login(self, request, app, token, **kwargs):
        uid = kwargs.get('response', {}).get('uid')
        resp = requests.get(self.get_profile_url(request), params={'access_token': token.token, 'uid': uid})
        extra_data = resp.json()
        return self.sociallogin_from_response(request, extra_data)

    def extract_uid(self, data):
        ret = data.get('idstr')
        if not ret:
            raise ProviderException("Missing 'idstr'")
        return ret

    def extract_common_fields(self, data):
        return dict(username=data.get('screen_name'), name=data.get('name'))


provider_classes = [WeiboProvider]
