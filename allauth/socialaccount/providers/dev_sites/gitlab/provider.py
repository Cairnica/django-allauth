# -*- coding: utf-8 -*-
import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.core.oauth2.provider import OAuth2Provider


class GitLabAccount(ProviderAccount):

    def get_profile_url(self):
        return self.account.extra_data.get('web_url')

    def get_avatar_url(self):
        return self.account.extra_data.get('avatar_url')

    def to_str(self):
        dflt = super(GitLabAccount, self).to_str()
        return self.account.extra_data.get('name', dflt)


class GitLabProvider(OAuth2Provider):
    id = 'gitlab'
    name = 'GitLab'
    account_class = GitLabAccount
    
    provider_base_url = 'https://gitlab.com'
    provider_api_version = 'v4'

    access_token_url = '{provider_base_url}/oauth/token'
    authorize_url = '{provider_base_url}/oauth/authorize'
    profile_url = '{provider_base_url}/api/{provider_api_version}/user'

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        return dict(
            email=data.get('email'),
            username=data.get('username'),
            name=data.get('name'),
        )

    def complete_login(self, request, app, token, response):
        extra_data = requests.get(self.get_profile_url(request), params={
            'access_token': token.token
        })

        return self.sociallogin_from_response(
            request,
            extra_data.json()
        )


provider_classes = [GitLabProvider]
