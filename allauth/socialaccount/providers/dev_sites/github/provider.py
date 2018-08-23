import requests

from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.core.oauth2.provider import OAuth2Provider


class GitHubAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('html_url')

    def get_avatar_url(self):
        return self.account.extra_data.get('avatar_url')

    def to_str(self):
        dflt = super(GitHubAccount, self).to_str()
        return next(
            value
            for value in (
                self.account.extra_data.get('name', None),
                self.account.extra_data.get('login', None),
                dflt
            )
            if value is not None
        )


class GitHubProvider(OAuth2Provider):
    id = 'github'
    name = 'GitHub'
    account_class = GitHubAccount
    
    access_token_url = '{GITHUB_URL}/login/oauth/access_token'
    authorize_url = '{GITHUB_URL}/login/oauth/authorize'
    profile_url = '{GITHUB_API_URL}/user'
    emails_url = '{GITHUB_API_URL}/user/emails'

    def get_default_scope(self):
        scope = []
        if app_settings.QUERY_EMAIL:
            scope.append('user:email')
        return scope

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        return dict(email=data.get('email'),
                    username=data.get('login'),
                    name=data.get('name'))

    def complete_login(self, request, app, token, **kwargs):
        params = {'access_token': token.token}
        resp = requests.get(self.get_profile_url(request), params=params)
        extra_data = resp.json()
        if app_settings.QUERY_EMAIL and not extra_data.get('email'):
            extra_data['email'] = self.get_email(token)
        return self.sociallogin_from_response(
            request, extra_data
        )

    def get_email(self, token):
        email = None
        params = {'access_token': token.token}
        resp = requests.get(self.emails_url, params=params)
        emails = resp.json()
        if resp.status_code == 200 and emails:
            email = emails[0]
            primary_emails = [
                e for e in emails
                if not isinstance(e, dict) or e.get('primary')
            ]
            if primary_emails:
                email = primary_emails[0]
            if isinstance(email, dict):
                email = email.get('email', '')
        return email


provider_classes = [GitHubProvider]
