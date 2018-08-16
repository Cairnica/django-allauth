import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class FoursquareAccount(ProviderAccount):
    def get_profile_url(self):
        return 'https://foursquare.com/user/' \
            + self.account.extra_data.get('id')

    def get_avatar_url(self):
        return self.account.extra_data.get('photo')

    def to_str(self):
        dflt = super(FoursquareAccount, self).to_str()
        return self.account.extra_data.get('name', dflt)


class FoursquareProvider(OAuth2Provider):
    id = 'foursquare'
    name = 'Foursquare'
    account_class = FoursquareAccount
    
    access_token_url = 'https://foursquare.com/oauth2/access_token'
    # Issue ?? -- this one authenticates over and over again...
    # authorize_url = 'https://foursquare.com/oauth2/authorize'
    authorize_url = 'https://foursquare.com/oauth2/authenticate'
    profile_url = 'https://api.foursquare.com/v2/users/self'

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        return dict(first_name=data.get('firstname'),
                    last_name=data.get('lastname'),
                    email=data.get('contact').get('email'))

    def complete_login(self, request, app, token, **kwargs):
        # Foursquare needs a version number for their API requests as
        # documented here
        # https://developer.foursquare.com/overview/versioning
        resp = requests.get(self.get_profile_url(request), params={'oauth_token': token.token, 'v': '20140116'})
        extra_data = resp.json()['response']['user']
        return self.sociallogin_from_response(request, extra_data)


provider_classes = [FoursquareProvider]
