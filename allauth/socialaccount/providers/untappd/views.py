from allauth.socialaccount.providers.oauth2.views import (
    OAuth2CallbackView,
)

from .client import UntappdOAuth2Client


class UntappdOAuth2CallbackView(OAuth2CallbackView):
    """ Custom OAuth2CallbackView to return UntappdOAuth2Client """

    def get_client(self, request, app):
        client = super(UntappdOAuth2CallbackView, self).get_client(request, app)
        untappd_client = UntappdOAuth2Client(
            client.request, client.consumer_key, client.consumer_secret,
            client.access_token_method, client.access_token_url,
            client.callback_url, client.scope
        )
        return untappd_client

