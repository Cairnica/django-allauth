from django.urls import reverse
from django.conf.urls import include, url
from django.utils.http import urlencode

from allauth.compat import parse_qsl
from allauth.socialaccount.providers.base import Provider
from allauth.utils import import_attribute

class OAuthProvider(Provider):

    @classmethod
    def get_urlpatterns(cls):
        login_view = import_attribute(cls.get_package() + '.views.oauth_login')
        callback_view = import_attribute(cls.get_package() + '.views.oauth_callback')

        urlpatterns = [
            url('^login/$', login_view, name=cls.id + "_login"),
            url('^login/callback/$', callback_view, name=cls.id + "_callback"),
        ]

        return [url('^' + cls.get_slug() + '/', include(urlpatterns))]

    def get_login_url(self, request, **kwargs):
        url = reverse(self.id + "_login")
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

    def get_scope(self, request):
        settings = self.get_settings()
        scope = settings.get('SCOPE')
        if scope is None:
            scope = self.get_default_scope()
        return scope

    def get_default_scope(self):
        return []
