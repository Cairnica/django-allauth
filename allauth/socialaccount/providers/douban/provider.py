import requests

from allauth.socialaccount.providers.base import ProviderAccount, ProviderException
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class DoubanAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('alt')

    def get_avatar_url(self):
        return self.account.extra_data.get('large_avatar')

    def to_str(self):
        dflt = super(DoubanAccount, self).to_str()
        return self.account.extra_data.get('name', dflt)


class DoubanProvider(OAuth2Provider):
    id = 'douban'
    name = 'Douban'
    account_class = DoubanAccount
    
    access_token_url = 'https://www.douban.com/service/auth2/token'
    authorize_url = 'https://www.douban.com/service/auth2/auth'
    profile_url = 'https://api.douban.com/v2/user/~me'

    def extract_uid(self, data):
        return data['id']

    def extract_common_fields(self, data):
        """
        Extract data from profile json to populate user instance.

        In Douban profile API:

        - id: a digital string, will never change
        - uid: defaults to id, but can be changed once, used in profile
          url, like slug
        - name: display name, can be changed every 30 days

        So we should use `id` as username here, other than `uid`.
        Also use `name` as `first_name` for displaying purpose.
        """
        return {
            'username': data['id'],
            'first_name': data.get('name', ''),
        }

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': 'Bearer %s' % token.token}
        resp = requests.get(self.get_profile_url(request), headers=headers)
        extra_data = resp.json()
        """
        Douban may return data like this:

            {
                'code': 128,
                'request': 'GET /v2/user/~me',
                'msg': 'user_is_locked:53358092'
            }

        """
        if 'id' not in extra_data:
            msg = extra_data.get('msg', _('Invalid profile data'))
            raise ProviderException(msg)
        return self.sociallogin_from_response(
            request, extra_data)


provider_classes = [DoubanProvider]
