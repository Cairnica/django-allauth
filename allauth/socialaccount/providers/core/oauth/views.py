from __future__ import absolute_import

from django.urls import reverse

from allauth.socialaccount import providers
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)
from allauth.socialaccount.models import SocialLogin, SocialToken
from allauth.socialaccount.providers.base import ProviderView
from allauth.socialaccount.providers.core.oauth.client import (
    OAuthClient,
    OAuthError,
)

from ..base import AuthAction, AuthError


class OAuthView(ProviderView):
    def _get_client(self, request, callback_url):
        provider = self.provider
        app = provider.get_app(request)
        scope = ' '.join(provider.get_scope(request))
        parameters = {}
        if scope:
            parameters['scope'] = scope
        client = OAuthClient(
            request, app.client_id, app.secret,
            provider.get_request_token_url(request),
            provider.get_access_token_url(request),
            callback_url,
            parameters=parameters, provider=provider
        )
        return client


class OAuthLoginView(OAuthView):
    def dispatch(self, request):
        provider = self.provider
        callback_url = reverse(provider.slug + "_callback")
        SocialLogin.stash_state(request)
        action = request.GET.get('action', AuthAction.AUTHENTICATE)
        auth_url = provider.get_auth_url(request, action) or provider.get_authorize_url(request)
        auth_params = provider.get_auth_params(request, action)
        client = self._get_client(request, callback_url)
        try:
            return client.get_redirect(auth_url, auth_params)
        except OAuthError as e:
            return render_authentication_error(request, provider.slug, exception=e)


class OAuthCallbackView(OAuthView):
    def dispatch(self, request):
        """
        View to handle final steps of OAuth based authentication where the user
        gets redirected back to from the service provider
        """
        provider = self.provider
        login_done_url = reverse(provider.slug + "_callback")
        client = self._get_client(request, login_done_url)
        if not client.is_valid():
            if 'denied' in request.GET:
                error = AuthError.CANCELLED
            else:
                error = AuthError.UNKNOWN
            extra_context = dict(oauth_client=client)
            return render_authentication_error(request, provider.slug, error=error, extra_context=extra_context)

        app = provider.get_app(request)

        try:
            access_token = client.get_access_token()
            token = SocialToken(
                app=app,
                token=access_token['oauth_token'],
                # .get() -- e.g. Evernote does not feature a secret
                token_secret=access_token.get('oauth_token_secret', '')
            )
            login = provider.complete_login(request, app, token, response=access_token)
            login.token = token
            login.state = SocialLogin.unstash_state(request)
            return complete_social_login(request, login)
        except OAuthError as e:
            return render_authentication_error(request, provider.slug, exception=e)
