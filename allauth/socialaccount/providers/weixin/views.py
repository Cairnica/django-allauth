import requests

from django.urls import reverse

from allauth.account import app_settings
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2CallbackView,
    OAuth2LoginView,
)
from allauth.utils import build_absolute_uri

from .client import WeixinOAuth2Client
from .provider import WeixinProvider


class WeixinOAuth2ClientMixin(object):

    def get_client(self, request, app):
        provider = self.provider
        callback_url = reverse(provider.slug + "_callback")
        protocol = (provider.redirect_uri_protocol or app_settings.DEFAULT_HTTP_PROTOCOL)
        callback_url = build_absolute_uri(request, callback_url, protocol=protocol)
        scope = provider.get_scope(request)
        client = WeixinOAuth2Client(
            self.request, app.client_id, app.secret,
            self.get_access_token_method(request),
            self.get_access_token_url(request),
            callback_url,
            scope
        )
        return client


class WeixinOAuth2LoginView(WeixinOAuth2ClientMixin, OAuth2LoginView):
    pass


class WeixinOAuth2CallbackView(WeixinOAuth2ClientMixin, OAuth2CallbackView):
    pass
