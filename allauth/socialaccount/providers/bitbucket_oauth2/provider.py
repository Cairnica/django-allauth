import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class BitbucketOAuth2Account(ProviderAccount):
    def get_profile_url(self):
        return (self.account.extra_data.get('links', {}).get('html', {}).get('href'))

    def get_avatar_url(self):
        return (self.account.extra_data.get('links', {}).get('avatar', {}).get('href'))

    def to_str(self):
        dflt = super(BitbucketOAuth2Account, self).to_str()
        return self.account.extra_data.get('display_name', dflt)


class BitbucketOAuth2Provider(OAuth2Provider):
    id = 'bitbucket_oauth2'
    name = 'Bitbucket'
    account_class = BitbucketOAuth2Account

    access_token_url = 'https://bitbucket.org/site/oauth2/access_token'
    authorize_url = 'https://bitbucket.org/site/oauth2/authorize'
    profile_url = 'https://api.bitbucket.org/2.0/user'
    emails_url = 'https://api.bitbucket.org/2.0/user/emails'

    def extract_uid(self, data):
        return data['username']

    def extract_common_fields(self, data):
        return dict(email=data.get('email'),
                    username=data.get('username'),
                    name=data.get('display_name'))

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.get_profile_url(request), params={'access_token': token.token})
        extra_data = resp.json()
        if app_settings.QUERY_EMAIL and not extra_data.get('email'):
            extra_data['email'] = self.get_email(token)
        return self.sociallogin_from_response(request, extra_data)

    def get_email(self, token):
        """Fetches email address from email API endpoint"""
        resp = requests.get(self.emails_url, params={'access_token': token.token})
        emails = resp.json().get('values', [])
        email = ''
        try:
            email = emails[0].get('email')
            primary_emails = [e for e in emails if e.get('is_primary', False)]
            email = primary_emails[0].get('email')
        except (IndexError, TypeError, KeyError):
            return ''
        finally:
            return email

provider_classes = [BitbucketOAuth2Provider]
