# -*- coding: utf-8 -*-
import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class Auth0Account(ProviderAccount):

    def get_avatar_url(self):
        return self.account.extra_data.get('picture')

    def to_str(self):
        dflt = super(Auth0Account, self).to_str()
        return self.account.extra_data.get('name', dflt)


class Auth0Provider(OAuth2Provider):
    id = 'auth0'
    name = 'Auth0'
    account_class = Auth0Account

    supports_state = True

    access_token_url = '{AUTH0_URL}/oauth/token'
    authorize_url = '{AUTH0_URL}/authorize'
    profile_url = '{AUTH0_URL}/userinfo'

    def get_default_scope(self):
        return ['openid', 'profile', 'email']

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        return {
            'email': data.get('email'),
            'username': data.get('username'),
            'name': data.get('name'),
            'user_id': data.get('user_id'),
            'picture': data.get('picture'),
        }

    def complete_login(self, request, app, token, response):
        extra_data = requests.get(self.get_profile_url(request), params={'access_token': token.token}).json()
        extra_data = {
            'user_id': extra_data['sub'],
            'id': extra_data['sub'],
            'name': extra_data['name'],
            'email': extra_data['email']
        }

        return self.sociallogin_from_response(request, extra_data)


provider_classes = [Auth0Provider]
