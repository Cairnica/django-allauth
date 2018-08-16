from datetime import datetime

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth.provider import OAuthProvider


class EvernoteAccount(ProviderAccount):
    def get_profile_url(self):
        return None

    def get_avatar_url(self):
        return None


class EvernoteProvider(OAuthProvider):
    id = 'evernote'
    name = 'Evernote'
    account_class = EvernoteAccount

    EVERNOTE_HOSTNAME = 'sandbox.evernote.com'

    request_token_url = 'https://{EVERNOTE_HOSTNAME}/oauth'
    access_token_url = 'https://{EVERNOTE_HOSTNAME}/oauth'
    authorize_url = 'https://{EVERNOTE_HOSTNAME}/OAuth.action'

    def extract_uid(self, data):
        return str(data['edam_userId'])

    def extract_common_fields(self, data):
        return data

    def complete_login(self, request, app, token, response):
        token.expires_at = datetime.fromtimestamp(int(response['edam_expires']) / 1000.0)
        extra_data = response
        return self.sociallogin_from_response(request, extra_data)


provider_classes = [EvernoteProvider]
