from django.urls import reverse
from django.conf.urls import url, include
from django.utils.http import urlencode

from allauth.socialaccount.providers.base import Provider, ProviderAccount, view_property

from .views import DraugiemLoginView, DraugiemCallbackView


class DraugiemAccount(ProviderAccount):

    def get_avatar_url(self):
        ret = None
        pic_small_url = self.account.extra_data.get('img')
        pic_icon_url = self.account.extra_data.get('imgi')
        pic_medium_url = self.account.extra_data.get('imgm')
        pic_large_url = self.account.extra_data.get('imgl')
        if pic_large_url:
            return pic_large_url
        elif pic_medium_url:
            return pic_medium_url
        elif pic_icon_url:
            return pic_icon_url
        elif pic_small_url:
            return pic_small_url
        else:
            return ret

    def to_str(self):
        default = super(DraugiemAccount, self).to_str()
        name = self.account.extra_data.get('name')
        surname = self.account.extra_data.get('surnname')

        if name and surname:
            return '%s %s' % (name, surname)

        return default


class DraugiemProvider(Provider):
    id = 'draugiem'
    name = 'Draugiem'
    account_class = DraugiemAccount

    class Factory(Provider.Factory):
        @view_property
        def login_view(self):
            return DraugiemLoginView

        @view_property
        def callback_view(self):
            return DraugiemCallbackView

        def get_urlpatterns(self):
            slug = self.slug

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

    def extract_uid(self, data):
        return str(data['uid'])

    def extract_common_fields(self, data):
        uid = self.extract_uid(data)
        user_data = data['users'][uid]
        return dict(first_name=user_data.get('name'),
                    last_name=user_data.get('surname'))

    def extract_extra_data(self, data):
        uid = self.extract_uid(data)
        return data['users'][uid]


provider_classes = [DraugiemProvider]
