import requests

from hashlib import md5
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class MailRuAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('link')

    def get_avatar_url(self):
        ret = None
        if self.account.extra_data.get('has_pic'):
            pic_big_url = self.account.extra_data.get('pic_big')
            pic_small_url = self.account.extra_data.get('pic_small')
            if pic_big_url:
                return pic_big_url
            elif pic_small_url:
                return pic_small_url
        else:
            return ret

    def to_str(self):
        dflt = super(MailRuAccount, self).to_str()
        return self.account.extra_data.get('name', dflt)


class MailRuProvider(OAuth2Provider):
    id = 'mailru'
    name = 'Mail.RU'
    account_class = MailRuAccount
    
    access_token_url = 'https://connect.mail.ru/oauth/token'
    authorize_url = 'https://connect.mail.ru/oauth/authorize'
    profile_url = 'http://www.appsmail.ru/platform/api'

    def complete_login(self, request, app, token, **kwargs):
        uid = kwargs['response']['x_mailru_vid']
        data = {
            'method': 'users.getInfo',
            'app_id': app.client_id,
            'secure': '1',
            'uids': uid
        }
        param_list = sorted(list(item + '=' + data[item] for item in data))
        data['sig'] = md5(
            (''.join(param_list) + app.secret).encode('utf-8')
        ).hexdigest()
        response = requests.get(self.get_profile_url(request), params=data)
        extra_data = response.json()[0]
        return self.sociallogin_from_response(request, extra_data)

    def extract_uid(self, data):
        return data['uid']

    def extract_common_fields(self, data):
        return dict(email=data.get('email'),
                    last_name=data.get('last_name'),
                    username=data.get('nick'),
                    first_name=data.get('first_name'))


provider_classes = [MailRuProvider]
