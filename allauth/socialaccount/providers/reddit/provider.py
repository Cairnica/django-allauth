import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class RedditAccount(ProviderAccount):
    def to_str(self):
        dflt = super(RedditAccount, self).to_str()
        name = self.account.extra_data.get('name', dflt)
        return name


class RedditProvider(OAuth2Provider):
    id = 'reddit'
    name = 'Reddit'
    account_class = RedditAccount

    authorize_url = 'https://www.reddit.com/api/v1/authorize'
    profile_url = 'https://oauth.reddit.com/api/v1/me'
    basic_auth = True

    @property
    def headers(self):
        # Allow custom User Agent to comply with reddit API limits
        return {'User-Agent': self.settings.get('USER_AGENT', 'django-allauth-header')}

    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": "bearer " + token.token}
        headers.update(self.headers)
        extra_data = requests.get(self.get_profile_url(request), headers=headers)

        # This only here because of weird response from the test suite
        if isinstance(extra_data, list):
            extra_data = extra_data[0]

        return self.sociallogin_from_response(
            request,
            extra_data.json()
        )

    def extract_uid(self, data):
        return data['name']

    def extract_common_fields(self, data):
        return dict(name=data.get('name'))

    def get_default_scope(self):
        scope = ['identity']
        return scope


provider_classes = [RedditProvider]
