import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class Scope(object):
    USERINFO_PROFILE = '/authenticate'


class OrcidAccount(ProviderAccount):
    def get_profile_url(self):
        return extract_from_dict(self.account.extra_data, ['orcid-identifier', 'uri'])

    def to_str(self):
        return self.account.uid


class OrcidProvider(OAuth2Provider):
    id = 'orcid'
    name = 'Orcid.org'
    account_class = OrcidAccount

    # http://support.orcid.org/knowledgebase/articles/335483-the-public-client-orcid-api

    base_domain = 'orcid.org'
    member_api = False

    authorize_url = 'https://{base_domain}/oauth/authorize'
    access_token_url = 'https://{api_domain}/oauth/token'
    profile_url = 'https://{api_domain}/v2.1/%s/record'

    @property
    def api_domain(self):
        return '{prefix}.{base_domain}'.format(prefix=('api' if self.member_api else 'pub'), base_domain=self.base_domain)

    def complete_login(self, request, app, token, **kwargs):
        params = {}
        if self.member_api:
            params['access_token'] = token.token

        resp = requests.get(self.get_profile_url(request) % kwargs['response']['orcid'], params=params, headers={'accept': 'application/orcid+json'})
        extra_data = resp.json()
        return self.sociallogin_from_response(request, extra_data)

    def get_default_scope(self):
        return [Scope.USERINFO_PROFILE]

    def extract_uid(self, data):
        return extract_from_dict(data, ['orcid-identifier', 'path'])

    def extract_common_fields(self, data):
        common_fields = dict(
            email=extract_from_dict(data, ['person', 'emails', 0, 'email']),
            last_name=extract_from_dict(data, ['person', 'name', 'family-name', 'value']),
            first_name=extract_from_dict(data, ['person', 'name', 'given-names', 'value']),)
        return dict((key, value) for (key, value) in common_fields.items() if value)


provider_classes = [OrcidProvider]


def extract_from_dict(data, path):
    """
    Navigate `data`, a multidimensional array (list or dictionary), and returns
    the object at `path`.
    """
    value = data
    try:
        for key in path:
            value = value[key]
        return value
    except (KeyError, IndexError, TypeError):
        return ''
