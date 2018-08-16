from django.conf.urls import url

from allauth.socialaccount.providers.base import Provider, ProviderAccount

from . import views


class TelegramAccount(ProviderAccount):
    pass


class TelegramProvider(Provider):
    id = 'telegram'
    name = 'Telegram'
    account_class = TelegramAccount

    class Factory(Provider.Factory):
        def get_urlpatterns(self):
            return [
                url('^telegram/login/$', views.telegram_login, name="telegram_login")
            ]

    def get_login_url(self, request, **kwargs):
        # TODO: Find a way to better wrap the iframed button
        return '#'

    def extract_uid(self, data):
        return data['id']


provider_classes = [TelegramProvider]
