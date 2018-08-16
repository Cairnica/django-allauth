import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class DiscordAccount(ProviderAccount):
    def to_str(self):
        dflt = super(DiscordAccount, self).to_str()
        return self.account.extra_data.get('username', dflt)


class DiscordProvider(OAuth2Provider):
    id = 'discord'
    name = 'Discord'
    account_class = DiscordAccount
    
    access_token_url = 'https://discordapp.com/api/oauth2/token'
    authorize_url = 'https://discordapp.com/api/oauth2/authorize'
    profile_url = 'https://discordapp.com/api/users/@me'

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        return dict(
            email=data.get('email'),
            username=data.get('username'),
            name=data.get('username'),
        )

    def get_default_scope(self):
        return ['email', 'identify']

    def complete_login(self, request, app, token, **kwargs):
        headers = {
            'Authorization': 'Bearer {0}'.format(token.token),
            'Content-Type': 'application/json',
        }
        extra_data = requests.get(self.get_profile_url(request), headers=headers)

        return self.sociallogin_from_response(
            request,
            extra_data.json()
        )


provider_classes = [DiscordProvider]
