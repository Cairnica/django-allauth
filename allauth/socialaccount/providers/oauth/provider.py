from django.urls import reverse
from django.conf.urls import include, url
from django.utils.http import urlencode
from django.utils.functional import cached_property

from allauth.compat import parse_qsl
from allauth.socialaccount.providers.base import Provider
from allauth.utils import import_attribute

from .views import OAuthLoginView, OAuthCallbackView

class OAuthProvider(Provider):
    adapter_class = None
    login_view_class = OAuthLoginView
    callback_view_class = OAuthCallbackView

    def create_adapter(self, request):
        return self.adapter_class(request, self)

    @cached_property
    def login_view(self):
        if self.adapter_class:
            return self.login_view_class.adapter_view(self)
        return import_attribute(self.get_package() + '.views.oauth_login')

    @cached_property
    def callback_view(self):
        if self.adapter_class:
            return self.callback_view_class.adapter_view(self)
        return import_attribute(self.get_package() + '.views.oauth_callback')

    def get_urlpatterns(self):
        slug = self.get_slug()

        urlpatterns = [
            url(r'^login/$', self.login_view, name=slug + "_login"),
            url(r'^login/callback/$', self.callback_view, name=slug + "_callback"),
        ]

        return [url('^' + slug + '/', include(urlpatterns))]

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
