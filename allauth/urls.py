from django.conf.urls import include, url

from allauth.socialaccount import providers

from . import app_settings


urlpatterns = [url(r'^', include('allauth.account.urls'))]

if app_settings.SOCIALACCOUNT_ENABLED:
    urlpatterns += [url(r'^social/', include('allauth.socialaccount.urls'))]

for provider in providers.registry.get_list():
    urlpatterns += provider.get_urlpatterns()
