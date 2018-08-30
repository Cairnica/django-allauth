# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from allauth.socialaccount.providers import registry
from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse,TestCase

from .provider import RedditProvider


class RedditTests(OAuth2TestsMixin, TestCase):
    provider_class = RedditProvider
    
    def get_mocked_response(self):
        return [MockedResponse(200, """{
        "name": "wayward710"}""")]
