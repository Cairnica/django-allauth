import requests
from hashlib import md5

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


USER_FIELDS = ['uid',
               'locale',
               'first_name',
               'last_name',
               'name',
               'gender',
               'age',
               'birthday',
               'has_email',
               'current_status',
               'current_status_id',
               'current_status_date',
               'online',
               'photo_id',
               'pic_1',  # aka pic50x50
               'pic_2',  # aka pic128max
               'pic190x190',  # small
               'pic640x480',  # medium
               'pic1024x768',  # big
               'location']


class OdnoklassnikiAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('link')

    def get_avatar_url(self):
        ret = None
        pic_big_url = self.account.extra_data.get('pic1024x768')
        pic_medium_url = self.account.extra_data.get('pic640x480')
        pic_small_url = self.account.extra_data.get('pic190x190')
        if pic_big_url:
            return pic_big_url
        elif pic_medium_url:
            return pic_medium_url
        elif pic_small_url:
            return pic_small_url
        else:
            return ret

    def to_str(self):
        dflt = super(OdnoklassnikiAccount, self).to_str()
        return self.account.extra_data.get('name', dflt)


class OdnoklassnikiProvider(OAuth2Provider):
    id = 'odnoklassniki'
    name = 'Odnoklassniki'
    account_class = OdnoklassnikiAccount

    access_token_url = 'http://api.odnoklassniki.ru/oauth/token.do'
    authorize_url = 'http://www.odnoklassniki.ru/oauth/authorize'
    profile_url = 'http://api.odnoklassniki.ru/fb.do'
    access_token_method = 'POST'

    def complete_login(self, request, app, token, **kwargs):
        data = {'method': 'users.getCurrentUser',
                'access_token': token.token,
                'fields': ','.join(USER_FIELDS),
                'format': 'JSON',
                'application_key': app.key}
        suffix = md5('{0:s}{1:s}'.format(data['access_token'], app.secret).encode('utf-8')).hexdigest()
        check_list = sorted(['{0:s}={1:s}'.format(k, v) for k, v in data.items() if k != 'access_token'])
        data['sig'] = md5((''.join(check_list) + suffix).encode('utf-8')).hexdigest()

        response = requests.get(self.get_profile_url(request), params=data)
        extra_data = response.json()
        return self.sociallogin_from_response(request, extra_data)

    def extract_uid(self, data):
        return data['uid']

    def extract_common_fields(self, data):
        return dict(last_name=data.get('last_name'),
                    first_name=data.get('first_name'))


provider_classes = [OdnoklassnikiProvider]
