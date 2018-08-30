from django.test.utils import override_settings
from django.urls import reverse

from allauth.tests import TestCase, patch
from allauth.utils import get_user_model
from allauth.socialaccount.tests import ProviderTestsMixin

from .provider import PersonaProvider


class PersonaTests(ProviderTestsMixin, TestCase):
    provider_class = PersonaProvider
    provider_settings = {'audience': 'https://www.example.com:433'}

    def test_login(self):
        with patch('allauth.socialaccount.providers.core.persona.views.requests') as requests_mock:
            requests_mock.post.return_value.json.return_value = {
                'status': 'okay',
                'email': 'persona@example.com'
            }

            resp = self.client.post(reverse('persona_login'), dict(assertion='dummy'))
            self.assertRedirects(resp, '/accounts/profile/', fetch_redirect_response=False)
            get_user_model().objects.get(email='persona@example.com')
