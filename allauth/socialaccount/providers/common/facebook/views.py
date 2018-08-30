import logging
import requests
from datetime import timedelta

from django.utils import timezone

from allauth.socialaccount import app_settings, providers
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)
from allauth.socialaccount.models import SocialLogin, SocialToken
from allauth.socialaccount.providers.core.oauth2.views import (
    ProviderView,
    OAuth2View,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .forms import FacebookConnectForm


logger = logging.getLogger(__name__)


class FacebookLoginByTokenView(ProviderView):
    def dispatch(self, request):
        ret = None
        auth_exception = None
        if request.method == 'POST':
            form = FacebookConnectForm(request.POST)
            if form.is_valid():
                try:
                    provider = self.provider
                    login_options = provider.get_fb_login_options(request)
                    app = provider.get_app(request)
                    access_token = form.cleaned_data['access_token']
                    expires_at = None
                    
                    if login_options.get('auth_type') == 'reauthenticate':
                        info = requests.get(f'{provider.base_graph_url}/oauth/access_token_info', params={'client_id': app.client_id, 'access_token': access_token}).json()
                        nonce = provider.get_nonce(request, pop=True)
                        ok = nonce and nonce == info.get('auth_nonce')
                    else:
                        ok = True

                    if ok and provider.get_settings().get('EXCHANGE_TOKEN'):
                        resp = requests.get(
                            '{provider.base_graph_url}/oauth/access_token',
                            params={
                                'grant_type': 'fb_exchange_token',
                                'client_id': app.client_id,
                                'client_secret': app.secret,
                                'fb_exchange_token': access_token
                            }).json()
                        access_token = resp['access_token']
                        expires_in = resp.get('expires_in')
                        if expires_in:
                            expires_at = timezone.now() + timedelta(seconds=int(expires_in))
                    if ok:
                        token = SocialToken(app=app, token=access_token, expires_at=expires_at)
                        login = provider.complete_login(request, app, token)
                        login.token = token
                        login.state = SocialLogin.state_from_request(request)
                        ret = complete_social_login(request, login)
                except requests.RequestException as e:
                    logger.exception('Error accessing FB user profile')
                    auth_exception = e
        if not ret:
            ret = render_authentication_error(request, provider.id, exception=auth_exception)
        return ret
