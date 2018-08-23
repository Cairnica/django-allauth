from __future__ import unicode_literals

import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.core.oauth2.provider import OAuth2Provider


LOGIN_URL = 'https://login.microsoftonline.com/common/oauth2/v2.0'
GRAPH_URL = 'https://graph.microsoft.com/v1.0'


class AzureAccount(ProviderAccount):

    # TODO:
    # - avatar_url:
    #   https://developer.microsoft.com/en-us/graph/docs/api-reference/beta/api/profilephoto_get  # noqa
    def get_username(self):
        return self.account.extra_data['email']

    def to_str(self):
        name = '{0} {1}'.format(self.account.extra_data.get('first_name', ''),
                                self.account.extra_data.get('last_name', ''))
        if name.strip() != '':
            return name
        return super(AzureAccount, self).to_str()


class AzureProvider(OAuth2Provider):
    id = str('azure')
    name = 'Azure'
    account_class = AzureAccount

    access_token_url = LOGIN_URL + '/token'
    authorize_url = LOGIN_URL + '/authorize'
    profile_url = 'https://graph.microsoft.com/v1.0/me'

    # Can be used later to obtain group data. Needs 'Group.Read.All' or similar.
    # See https://developer.microsoft.com/en-us/graph/docs/api-reference/beta/api/user_list_memberof  # noqa
    groups_url = GRAPH_URL + '/me/memberOf?$select=displayName'

    def get_default_scope(self):
        """
        Doc on scopes available at
        https://docs.microsoft.com/en-us/azure/active-directory/develop/active-directory-v2-scopes  # noqa
        """
        return ['User.Read', 'openid']

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        email = data.get('mail')
        if not email and 'userPrincipalName' in data:
            email = data.get('userPrincipalName')
        return dict(email=email,
                    username=email,
                    last_name=data.get('surname'),
                    first_name=data.get('givenName'))

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': 'Bearer {0}'.format(token.token)}
        extra_data = {}

        resp = requests.get(self.get_profile_url(request), headers=headers)

        # See:
        #
        # https://developer.microsoft.com/en-us/graph/docs/api-reference/v1.0/api/user_get  # noqa
        #
        # example of what's returned (in python format)
        #
        # {u'displayName': u'John Smith', u'mobilePhone': None,
        #  u'preferredLanguage': u'en-US', u'jobTitle': u'Director',
        #  u'userPrincipalName': u'john@smith.com',
        #  u'@odata.context':
        #  u'https://graph.microsoft.com/v1.0/$metadata#users/$entity',
        #  u'officeLocation': u'Paris', u'businessPhones': [],
        #  u'mail': u'john@smith.com', u'surname': u'Smith',
        #  u'givenName': u'John', u'id': u'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'}

        profile_data = resp.json()
        extra_data.update(profile_data)

        return self.sociallogin_from_response(request, extra_data)


provider_classes = [AzureProvider]
