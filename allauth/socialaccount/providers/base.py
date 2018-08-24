from importlib import import_module
import functools

from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.views.generic import View

from allauth.exceptions import ImmediateHttpResponse
from allauth.account.models import EmailAddress
from allauth.socialaccount import app_settings

from ..adapter import get_adapter


class AuthProcess(object):
    LOGIN = 'login'
    CONNECT = 'connect'
    REDIRECT = 'redirect'


class AuthAction(object):
    AUTHENTICATE = 'authenticate'
    REAUTHENTICATE = 'reauthenticate'


class AuthError(object):
    UNKNOWN = 'unknown'
    CANCELLED = 'cancelled'  # Cancelled on request of user
    DENIED = 'denied'  # Denied by server


class ProviderException(Exception):
    pass


def view_property(func):
    @functools.wraps(func)
    def new_func(self):
        return func(self).adapter_view(self)
    return cached_property(new_func)


class Provider(object):
    default_settings = None
    account_class = None

    def __init__(self, factory, request=None):
        self.factory = factory
        self.request = request

    class Factory():
        def __init__(self, ProviderClass, id=None, **kwargs):
            self.id = id or Provider.__name__
            self.provider_class = ProviderClass

        @property
        def settings(self):
            return dict().update(self.provider_class.default_settings, app_settings.PROVIDERS.get(self.id, {}))

        @property
        def slug(self):
            return self.id

        def create_provider(self, current_request):
            return self.provider_class(current_request)

        def get_urlpatterns(self):
            try:
                prov_mod = import_module(self.provider_class.get_package() + '.urls')
            except ImportError:
                return []
            return getattr(prov_mod, 'urlpatterns', [])


    @property
    def id(self):
        return self.factory.id

    @property
    def slug(self):
        return self.factory.slug

    def get_login_url(self, request, next=None, **kwargs):
        """
        Builds the URL to redirect to when initiating a login for this
        provider.
        """
        raise NotImplementedError("get_login_url() for " + self.name)

    def get_app(self, request):
        # NOTE: Avoid loading models at top due to registry boot...
        from allauth.socialaccount.models import SocialApp

        return SocialApp.objects.get_current(self.id, request)

    def media_js(self, request):
        """
        Some providers may require extra scripts (e.g. a Facebook connect)
        """
        return ''

    def wrap_account(self, social_account):
        return self.account_class(social_account)

    def get_settings(self):
        return self.factory.settings

    @property
    def settings(self):
        return self.factory.settings

    def sociallogin_from_response(self, request, response):
        """
        Instantiates and populates a `SocialLogin` model based on the data
        retrieved in `response`. The method does NOT save the model to the
        DB.

        Data for `SocialLogin` will be extracted from `response` with the
        help of the `.extract_uid()`, `.extract_extra_data()`,
        `.extract_common_fields()`, and `.extract_email_addresses()`
        methods.

        :param request: a Django `HttpRequest` object.
        :param response: object retrieved via the callback response of the
            social auth provider.
        :return: A populated instance of the `SocialLogin` model (unsaved).
        """
        # NOTE: Avoid loading models at top due to registry boot...
        from allauth.socialaccount.models import SocialLogin, SocialAccount

        adapter = get_adapter(request)
        uid = self.extract_uid(response)
        extra_data = self.extract_extra_data(response)
        common_fields = self.extract_common_fields(response)
        socialaccount = SocialAccount(extra_data=extra_data,
                                      uid=uid,
                                      provider=self.id)
        email_addresses = self.extract_email_addresses(response)
        self.cleanup_email_addresses(common_fields.get('email'),
                                     email_addresses)
        sociallogin = SocialLogin(account=socialaccount,
                                  email_addresses=email_addresses)
        user = sociallogin.user = adapter.new_user(request, sociallogin)
        user.set_unusable_password()
        adapter.populate_user(request, sociallogin, common_fields)
        return sociallogin

    def extract_uid(self, data):
        """
        Extracts the unique user ID from `data`
        """
        raise NotImplementedError(
            'The provider must implement the `extract_uid()` method'
        )

    def extract_extra_data(self, data):
        """
        Extracts fields from `data` that will be stored in
        `SocialAccount`'s `extra_data` JSONField.

        :return: any JSON-serializable Python structure.
        """
        return data

    def extract_common_fields(self, data):
        """
        Extracts fields from `data` that will be used to populate the
        `User` model in the `SOCIALACCOUNT_ADAPTER`'s `populate_user()`
        method.

        For example:

            {'first_name': 'John'}

        :return: dictionary of key-value pairs.
        """
        return {}

    def cleanup_email_addresses(self, email, addresses):
        # Move user.email over to EmailAddress
        if (email and email.lower() not in [
                a.email.lower() for a in addresses]):
            addresses.append(EmailAddress(email=email,
                                          verified=False,
                                          primary=True))
        # Force verified emails
        settings = self.get_settings()
        verified_email = settings.get('VERIFIED_EMAIL', False)
        if verified_email:
            for address in addresses:
                address.verified = True

    def extract_email_addresses(self, data):
        """
        For example:

        [EmailAddress(email='john@example.com',
                      verified=True,
                      primary=True)]
        """
        return []

    @classmethod
    def get_package(cls):
        pkg = getattr(cls, 'package', None)
        if not pkg:
            pkg = cls.__module__.rpartition('.')[0]
        return pkg


@python_2_unicode_compatible
class ProviderAccount(object):
    def __init__(self, social_account):
        self.account = social_account

    def get_profile_url(self):
        return None

    def get_avatar_url(self):
        return None

    def get_brand(self):
        """
        Returns a dict containing an id and name identifying the
        brand. Useful when displaying logos next to accounts in
        templates.

        For most providers, these are identical to the provider. For
        OpenID however, the brand can derived from the OpenID identity
        url.
        """
        provider = self.account.get_provider()
        return dict(id=provider.id,
                    name=provider.name)

    def __str__(self):
        return self.to_str()

    def to_str(self):
        """
        Due to the way python_2_unicode_compatible works, this does not work:

            @python_2_unicode_compatible
            class GoogleAccount(ProviderAccount):
                def __str__(self):
                    dflt = super(GoogleAccount, self).__str__()
                    return self.account.extra_data.get('name', dflt)

        It will result in and infinite recursion loop. That's why we
        add a method `to_str` that can be overriden in a conventional
        fashion, without having to worry about @python_2_unicode_compatible
        """
        return self.get_brand()['name']


class ProviderView(View):
    @classmethod
    def provider_view(cls, provider_factory):
        def view(request, *args, **kwargs):
            self = cls()
            self.request = request
            self.provider = provider_factory.create_provider(request)
            try:
                return self.dispatch(request, *args, **kwargs)
            except ImmediateHttpResponse as e:
                return e.response
        return view