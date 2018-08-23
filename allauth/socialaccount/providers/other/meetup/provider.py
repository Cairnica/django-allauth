import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.core.oauth2.provider import OAuth2Provider


class MeetupAccount(ProviderAccount):
    pass


class MeetupProvider(OAuth2Provider):
    id = 'meetup'
    name = 'Meetup'
    account_class = MeetupAccount
    
    access_token_url = 'https://secure.meetup.com/oauth2/access'
    authorize_url = 'https://secure.meetup.com/oauth2/authorize'
    profile_url = 'https://api.meetup.com/2/member/self'

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.get_profile_url(request), params={'access_token': token.token})
        extra_data = resp.json()
        return self.sociallogin_from_response(request, extra_data)

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        return dict(email=data.get('email'),
                    name=data.get('name'))


provider_classes = [MeetupProvider]
