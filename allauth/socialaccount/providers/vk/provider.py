import requests

from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter


class VKAccount(ProviderAccount):
    def get_profile_url(self):
        return 'https://vk.com/id%s' % self.account.extra_data.get('uid')

    def get_avatar_url(self):
        ret = None
        photo_big_url = self.account.extra_data.get('photo_big')
        photo_medium_url = self.account.extra_data.get('photo_medium')
        if photo_big_url:
            return photo_big_url
        elif photo_medium_url:
            return photo_medium_url
        else:
            return ret

    def to_str(self):
        first_name = self.account.extra_data.get('first_name', '')
        last_name = self.account.extra_data.get('last_name', '')
        name = ' '.join([first_name, last_name]).strip()
        return name or super(VKAccount, self).to_str()


class VKOAuth2Adapter(OAuth2Adapter):
    
    access_token_url = 'https://oauth.vk.com/access_token'
    authorize_url = 'https://oauth.vk.com/authorize'
    profile_url = 'https://api.vk.com/method/users.get'

    def complete_login(self, request, app, token, **kwargs):
        uid = kwargs['response'].get('user_id')
        params = {
            'v': '3.0',
            'access_token': token.token,
            'fields': ','.join(USER_FIELDS),
        }
        if uid:
            params['user_ids'] = uid
        resp = requests.get(self.get_profile_url(request),
                            params=params)
        resp.raise_for_status()
        extra_data = resp.json()['response'][0]
        email = kwargs['response'].get('email')
        if email:
            extra_data['email'] = email
        return self.sociallogin_from_response(request,
                                                             extra_data)


class VKProvider(OAuth2Provider):
    id = 'vk'
    name = 'VK'
    account_class = VKAccount
    adapter_class = VKOAuth2Adapter

    def get_default_scope(self):
        scope = []
        if app_settings.QUERY_EMAIL:
            scope.append('email')
        return scope

    def extract_uid(self, data):
        return str(data['uid'])

    def extract_common_fields(self, data):
        return dict(email=data.get('email'),
                    last_name=data.get('last_name'),
                    username=data.get('screen_name'),
                    first_name=data.get('first_name'))


provider_classes = [VKProvider]
