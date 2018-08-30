from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from openid.consumer import consumer
from openid.consumer.discover import DiscoveryFailure
from openid.extensions.ax import AttrInfo, FetchRequest
from openid.extensions.sreg import SRegRequest

from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import AuthError, ProviderView
from allauth.socialaccount.app_settings import QUERY_EMAIL
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)
from allauth.socialaccount.models import SocialLogin

from .forms import LoginForm
from .utils import AXAttributes, DBOpenIDStore, JSONSafeSession, SRegFields


def _openid_consumer(request):
    store = DBOpenIDStore()
    client = consumer.Consumer(JSONSafeSession(request.session), store)
    return client

class OpenIDLoginView(ProviderView):

    def dispatch(self, request):
        if 'openid' in request.GET or request.method == 'POST':
            form = LoginForm(
                dict(list(request.GET.items()) + list(request.POST.items()))
            )
            if form.is_valid():
                client = _openid_consumer(request)
                try:
                    auth_request = client.begin(form.cleaned_data['openid'])
                    provider = self.provider
                    app = provider.get_app(request)

                    if QUERY_EMAIL:
                        sreg = SRegRequest()
                        for name in SRegFields:
                            sreg.requestField(field_name=name, required=True)
                        auth_request.addExtension(sreg)
                        ax = FetchRequest()
                        for name in AXAttributes:
                            ax.add(AttrInfo(name, required=True))
                        server_settings = provider.get_server_settings(request.GET.get('openid'))
                        extra_attributes = server_settings.get('extra_attributes', [])
                        for _, name, required in extra_attributes:
                            ax.add(AttrInfo(name, required=required))
                        auth_request.addExtension(ax)

                    callback_url = provider.get_callback_url(request, app)
                    SocialLogin.stash_state(request)
                    # https://github.com/pennersr/django-allauth/issues/1523
                    auth_request.return_to_args['next'] = \
                        form.cleaned_data.get('next', '/')
                    redirect_url = auth_request.redirectURL(
                        request.build_absolute_uri('/'),
                        request.build_absolute_uri(callback_url))
                    return HttpResponseRedirect(redirect_url)
                # UnicodeDecodeError:
                # see https://github.com/necaris/python3-openid/issues/1
                except (UnicodeDecodeError, DiscoveryFailure) as e:
                    if request.method == 'POST':
                        form._errors["openid"] = form.error_class([e])
                    else:
                        return render_authentication_error(request, self.provider.id, exception=e)
        else:
            form = LoginForm(initial={
                'next': request.GET.get('next'),
                'process': request.GET.get('process')
            })
        d = dict(form=form)
        return render(request, "openid/login.html", d)


# @csrf_exempt
class OpenIDCallbackView(ProviderView):
    def dispatch(self, request):
        client = _openid_consumer(request)
        response = client.complete(
            dict(list(request.GET.items()) + list(request.POST.items())),
            request.build_absolute_uri(request.path))
        if response.status == consumer.SUCCESS:
            login = self.provider.sociallogin_from_response(request, response)
            login.state = SocialLogin.unstash_state(request)
            ret = complete_social_login(request, login)
        else:
            if response.status == consumer.CANCEL:
                error = AuthError.CANCELLED
            else:
                error = AuthError.UNKNOWN
            ret = render_authentication_error(request, self.provider.id, error=error)
        return ret
