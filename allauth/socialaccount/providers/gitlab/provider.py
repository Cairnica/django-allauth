# -*- coding: utf-8 -*-
import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter


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

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        return dict(
            email=data.get('email'),
            username=data.get('username'),
            name=data.get('name'),
        )


provider_classes = [GitLabProvider]
