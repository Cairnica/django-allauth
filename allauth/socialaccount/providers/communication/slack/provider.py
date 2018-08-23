import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.core.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.core.oauth2.provider import OAuth2Provider


class SlackAccount(ProviderAccount):
    def get_avatar_url(self):
        return self.account.extra_data.get('user').get('image_192', None)

    def to_str(self):
        dflt = super(SlackAccount, self).to_str()
        return '%s (%s)' % (
            self.account.extra_data.get('name', ''),
            dflt,
        )


class SlackProvider(OAuth2Provider):
    id = 'slack'
    name = 'Slack'
    account_class = SlackAccount

    access_token_url = 'https://slack.com/api/oauth.access'
    authorize_url = 'https://slack.com/oauth/authorize'
    identity_url = 'https://slack.com/api/auth.test'

    def complete_login(self, request, app, token, **kwargs):
        extra_data = self.get_data(token.token)
        return self.sociallogin_from_response(request, extra_data)

    def get_data(self, token):
        # Verify the user first
        resp = requests.get(
            self.identity_url,
            params={'token': token}
        )
        resp = resp.json()

        if not resp.get('ok'):
            raise OAuth2Error()

        # Fill in their generic info
        info = {
            'name': resp.get('user'),
            'user': {
                'name': resp.get('user'),
                'id': resp.get('user_id')
            },
            'team': {
                'name': resp.get('team'),
                'id': resp.get('team_id')
            }
        }

        return info

    def extract_uid(self, data):
        return "%s_%s" % (str(data.get('team').get('id')), str(data.get('user').get('id')))

    def extract_common_fields(self, data):
        return dict(name=data.get('name'), email=data.get('user').get('email', None))

    def get_default_scope(self):
        return ['identify']


provider_classes = [SlackProvider]
