from .provider import DiscordProvider
from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase


class DiscordTests(OAuth2TestsMixin, TestCase):
    provider_class = DiscordProvider

    def get_mocked_response(self):
        return MockedResponse(200, """{
            "id": "80351110224678912",
            "username": "Nelly",
            "discriminator": "1337",
            "avatar": "8342729096ea3675442027381ff50dfe",
            "verified": true,
            "email": "nelly@example.com"
        }""")
