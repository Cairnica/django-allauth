from datetime import timedelta

from django.urls import reverse
from django.conf.urls import include, url
from django.utils import timezone
from django.utils.http import urlencode
from django.utils.functional import cached_property

from allauth.compat import parse_qsl
from allauth.socialaccount.providers.base import Provider, view_property
from allauth.socialaccount.models import SocialLogin, SocialToken
from allauth.utils import build_absolute_uri
from allauth.utils import import_attribute

from .views import OAuth2LoginView, OAuth2CallbackView


class OAuth2Provider(Provider):
    expires_in_key = 'expires_in'
    supports_state = True
    redirect_uri_protocol = None
    access_token_method = 'POST'
    login_cancelled_error = 'access_denied'
    scope_delimiter = ' '
    basic_auth = False
    headers = None

    access_token_url = None
    authorize_url = None
    profile_url = None

    login_view_class = OAuth2LoginView
    callback_view_class = OAuth2CallbackView

    class Factory(Provider.Factory):
        @view_property
        def login_view(self):
            return self.provider_class.login_view_class

        @view_property
        def callback_view(self):
            return self.provider_class.callback_view_class

        def get_urlpatterns(self):
            slug = self.slug

            urlpatterns = [
                url(r'^login/$', self.login_view, name=slug + "_login"),
                url(r'^login/callback/$', self.callback_view, name=slug + "_callback"),
            ]

            return [url('^' + slug + '/', include(urlpatterns))]


    def get_access_token_url(self, callback_request):
        """ Get the remote URL to fetch the OAuth2 Token """
        return self.access_token_url.format_map(self)

    def get_authorize_url(self, login_request):
        """ Get the remote URL begin OAuth2 Authorization """
        return self.authorize_url.format_map(self)

    def get_profile_url(self, request):
        """ Get the remote URL to get the Profile """
        return self.profile_url.format_map(self)

    def get_login_url(self, request, **kwargs):
        """ Get the local URL to begin login """
        url = reverse(self.slug + "_login")
        if kwargs:
            url = url + '?' + urlencode(kwargs)
        return url
    
    def get_callback_url(self, login_request, app):
        """ Get the local URL for the OAuth2 callback """
        callback_url = reverse(self.slug + "_callback")
        protocol = self.redirect_uri_protocol
        return build_absolute_uri(login_request, callback_url, protocol)

    def get_auth_params(self, request, action):
        settings = self.get_settings()
        ret = dict(settings.get('AUTH_PARAMS', {}))
        dynamic_auth_params = request.GET.get('auth_params', None)
        if dynamic_auth_params:
            ret.update(dict(parse_qsl(dynamic_auth_params)))
        return ret

    def complete_login(self, request, app, access_token, **kwargs):
        """
        Returns a SocialLogin instance
        """
        raise NotImplementedError

    def parse_token(self, data):
        token = SocialToken(token=data['access_token'])
        token.token_secret = data.get('refresh_token', '')
        expires_in = data.get(self.expires_in_key, None)
        if expires_in:
            token.expires_at = timezone.now() + timedelta(seconds=int(expires_in))
        return token

    def get_scope(self, request):
        settings = self.get_settings()
        scope = list(settings.get('SCOPE', self.get_default_scope()))
        dynamic_scope = request.GET.get('scope', None)
        if dynamic_scope:
            scope.extend(dynamic_scope.split(','))
        return scope

    def get_default_scope(self):
        return []
