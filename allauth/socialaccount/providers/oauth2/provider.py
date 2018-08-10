from django.urls import reverse
from django.conf.urls import include, url
from django.utils.http import urlencode

from allauth.compat import parse_qsl
from allauth.socialaccount.providers.base import Provider
from allauth.utils import import_attribute


class OAuth2Provider(Provider):

    @classmethod
    def get_urlpatterns(cls):
        login_view = import_attribute(cls.get_package() + '.views.oauth2_login')
        callback_view = import_attribute(cls.get_package() + '.views.oauth2_callback')

        urlpatterns = [
            url(r'^login/$', login_view, name=cls.id + "_login"),
            url(r'^login/callback/$', callback_view, name=cls.id + "_callback"),
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

    def get_scope(self, request):
        settings = self.get_settings()
        scope = list(settings.get('SCOPE', self.get_default_scope()))
        dynamic_scope = request.GET.get('scope', None)
        if dynamic_scope:
            scope.extend(dynamic_scope.split(','))
        return scope

    def get_default_scope(self):
        return []
