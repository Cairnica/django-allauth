from __future__ import absolute_import

from datetime import timedelta
from requests import RequestException

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone

from allauth.socialaccount import providers
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)
from allauth.socialaccount.models import SocialLogin, SocialToken
from allauth.socialaccount.providers.base import ProviderException, ProviderView, AuthAction, AuthError
from allauth.socialaccount.providers.core.oauth2.client import (
    OAuth2Client,
    OAuth2Error,
)
from allauth.utils import build_absolute_uri, get_request_param


class OAuth2View(ProviderView):
    def get_client(self, request, app):
        provider = self.provider
        callback_url = provider.get_callback_url(request, app)
        scope = provider.get_scope(request)
        client = OAuth2Client(
            self.request, app.client_id, app.secret,
            provider.get_access_token_method(request),
            provider.get_access_token_url(request),
            callback_url,
            scope,
            scope_delimiter=provider.scope_delimiter,
            headers=provider.headers,
            basic_auth=provider.basic_auth
        )
        return client


class OAuth2LoginView(OAuth2View):
    def dispatch(self, request, *args, **kwargs):
        provider = self.provider
        app = provider.get_app(self.request)
        client = self.get_client(request, app)
        action = request.GET.get('action', AuthAction.AUTHENTICATE)
        auth_url = provider.get_authorize_url(request)
        auth_params = provider.get_auth_params(request, action)
        client.state = SocialLogin.stash_state(request)
        try:
            return HttpResponseRedirect(client.get_redirect_url(auth_url, auth_params))
        except OAuth2Error as e:
            return render_authentication_error(request, provider.id, exception=e)


class OAuth2CallbackView(OAuth2View):
    def dispatch(self, request, *args, **kwargs):
        provider = self.provider

        if 'error' in request.GET or 'code' not in request.GET:
            # Distinguish cancel from error
            auth_error = request.GET.get('error', None)
            if auth_error == provider.login_cancelled_error:
                error = AuthError.CANCELLED
            else:
                error = AuthError.UNKNOWN
            return render_authentication_error(request, provider.id, error=error)

        app = provider.get_app(self.request)
        client = self.get_client(request, app)

        try:
            access_token = client.get_access_token(request.GET['code'])
            token = provider.parse_token(access_token)
            token.app = app
            login = provider.complete_login(request, app, token, response=access_token)
            login.token = token
            if provider.supports_state:
                login.state = SocialLogin \
                    .verify_and_unstash_state(request, get_request_param(request, 'state'))
            else:
                login.state = SocialLogin.unstash_state(request)
            return complete_social_login(request, login)
        except (PermissionDenied, OAuth2Error, RequestException, ProviderException) as e:
            return render_authentication_error(request, provider.id, exception=e)
