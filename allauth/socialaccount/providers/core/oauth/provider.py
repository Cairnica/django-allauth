import re
from requests_oauthlib import OAuth1

from django.urls import reverse
from django.conf.urls import include, url
from django.template.base import Variable
from django.utils.http import urlencode
from django.utils.functional import cached_property

from allauth.compat import parse_qsl
from allauth.socialaccount.providers.base import Provider, view_property
from allauth.utils import import_attribute

from .views import OAuthLoginView, OAuthCallbackView

class OAuthProvider(Provider):
    login_view_class = OAuthLoginView
    callback_view_class = OAuthCallbackView

    request_token_url = None
    access_token_url = None
    authorize_url = None
    profile_url = None

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

    def format_url(self, url):
        def do_replace(match):
            return Variable(match.group(1)).resolve(self)
        return re.sub(r'{(.*?)}', do_replace, url)

    def get_request_token_url(self, callback_request):
        """ Get the remote URL to fetch the OAuth2 Token """
        return self.format_url(self.request_token_url)

    def get_access_token_url(self, callback_request):
        """ Get the remote URL to fetch the OAuth2 Token """
        return self.format_url(self.access_token_url)

    def get_authorize_url(self, login_request):
        """ Get the remote URL begin OAuth2 Authorization """
        return self.format_url(self.authorize_url)

    def get_profile_url(self, request):
        """ Get the remote URL to get the Profile """
        return self.format_url(self.profile_url)

    def get_login_url(self, request, **kwargs):
        url = reverse(self.slug + "_login")
        if kwargs:
            url = url + '?' + urlencode(kwargs)
        return url

    def get_auth_params(self, request, action):
        settings = self.get_settings()
        ret = dict(settings.get('AUTH_PARAMS', {}))
        dynamic_auth_params = request.GET.get('auth_params', None)
        if dynamic_auth_params:
            ret.update(dict(parse_qsl(dynamic_auth_params)))
        return ret

    def get_auth_url(self, request, action):
        # TODO: This is ugly. Move authorization_url away from the
        # adapter into the provider. Hmpf, the line between
        # adapter/provider is a bit too thin here.
        return None

    def complete_login(self, request, app, access_token, **kwargs):
        """
        Returns a SocialLogin instance
        """
        raise NotImplementedError

    def get_auth_header(self, social_app, access_token):
        return OAuth1(
            social_app.client_id,
            client_secret=social_app.secret,
            resource_owner_key=access_token.token,
            resource_owner_secret=access_token.token_secret
        )

    def get_scope(self, request):
        settings = self.get_settings()
        scope = settings.get('SCOPE')
        if scope is None:
            scope = self.get_default_scope()
        return scope

    def get_default_scope(self):
        return []
