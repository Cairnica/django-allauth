import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class TwitchAccount(ProviderAccount):
    def get_profile_url(self):
        return 'http://twitch.tv/' + self.account.extra_data.get('name')

    def get_avatar_url(self):
        return self.account.extra_data.get('logo')

    def to_str(self):
        dflt = super(TwitchAccount, self).to_str()
        return self.account.extra_data.get('name', dflt)


class TwitchProvider(OAuth2Provider):
    id = 'twitch'
    name = 'Twitch'
    account_class = TwitchAccount
    
    access_token_url = 'https://api.twitch.tv/kraken/oauth2/token'
    authorize_url = 'https://api.twitch.tv/kraken/oauth2/authorize'
    profile_url = 'https://api.twitch.tv/kraken/user'

    def complete_login(self, request, app, token, **kwargs):
        params = {"oauth_token": token.token, "client_id": app.client_id}
        response = requests.get(self.get_profile_url(request), params=params)

        data = response.json()
        if response.status_code >= 400:
            error = data.get("error", "")
            message = data.get("message", "")
            raise OAuth2Error("Twitch API Error: %s (%s)" % (error, message))

        if "_id" not in data:
            raise OAuth2Error("Invalid data from Twitch API: %r" % (data))

        return self.sociallogin_from_response(request, data)

    def extract_uid(self, data):
        return str(data['_id'])

    def extract_common_fields(self, data):
        return {
            "username": data.get("name"),
            "name": data.get("display_name"),
            "email": data.get("email"),
        }

    def get_default_scope(self):
        return ["user_read"]


provider_classes = [TwitchProvider]
