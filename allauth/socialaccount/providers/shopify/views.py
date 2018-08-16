from django.conf import settings
from django.http import HttpResponse

from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.providers.oauth2.views import OAuth2LoginView


class ShopifyOAuth2LoginView(OAuth2LoginView):
    def dispatch(self, request):
        response = super(ShopifyOAuth2LoginView, self).dispatch(request)

        is_embedded = getattr(settings, 'SOCIALACCOUNT_PROVIDERS', {}).get(
            'shopify', {}).get('IS_EMBEDDED', False)
        if is_embedded:
            """
            Shopify embedded apps (that run within an iFrame) require a JS
            (not server) redirect for starting the oauth2 process.

            See Also:
            https://help.shopify.com/api/sdks/embedded-app-sdk/getting-started#oauth
            """
            js = ''.join((
                '<!DOCTYPE html><html><head>'
                '<script type="text/javascript">',
                'window.top.location.href = "{url}";'.format(url=response.url),
                '</script></head><body></body></html>'
            ))
            response = HttpResponse(content=js)
            # Because this view will be within shopify's iframe
            response.xframe_options_exempt = True
        return response
