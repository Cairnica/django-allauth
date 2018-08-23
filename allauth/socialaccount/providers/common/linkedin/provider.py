from xml.etree import ElementTree
from xml.parsers.expat import ExpatError

from django.utils import six

from allauth.socialaccount import providers
from allauth.socialaccount.providers.core.oauth.client import OAuth
from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.core.oauth.provider import OAuthProvider


class LinkedInAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('public-profile-url')

    def get_avatar_url(self):
        # try to return the higher res picture-urls::(original) first
        try:
            if self.account.extra_data.get('picture-urls', {}).get(
                    'picture-url'):
                return self.account.extra_data.get('picture-urls', {}).get(
                    'picture-url')
        except Exception:
            # if we can't get higher res for any reason, we'll just return the
            # low res
            pass
        return self.account.extra_data.get('picture-url')

    def to_str(self):
        dflt = super(LinkedInAccount, self).to_str()
        name = self.account.extra_data.get('name', dflt)
        first_name = self.account.extra_data.get('first-name', None)
        last_name = self.account.extra_data.get('last-name', None)
        if first_name and last_name:
            name = first_name + ' ' + last_name
        return name


class LinkedInAPI(OAuth):
    url = 'https://api.linkedin.com/v1/people/~'

    def get_user_info(self):
        fields = providers.registry \
            .by_id(LinkedInProvider.id, self.request) \
            .get_profile_fields()
        url = self.url + ':(%s)' % ','.join(fields)
        raw_xml = self.query(url)
        if not six.PY3:
            raw_xml = raw_xml.encode('utf8')
        try:
            return self.to_dict(ElementTree.fromstring(raw_xml))
        except (ExpatError, KeyError, IndexError):
            return None

    def to_dict(self, xml):
        """
        Convert XML structure to dict recursively, repeated keys
        entries are returned as in list containers.
        """
        children = list(xml)
        if not children:
            return xml.text
        else:
            out = {}
            for node in list(xml):
                if node.tag in out:
                    if not isinstance(out[node.tag], list):
                        out[node.tag] = [out[node.tag]]
                    out[node.tag].append(self.to_dict(node))
                else:
                    out[node.tag] = self.to_dict(node)
            return out


class LinkedInProvider(OAuthProvider):
    id = 'linkedin'
    name = 'LinkedIn'
    account_class = LinkedInAccount
    
    request_token_url = 'https://api.linkedin.com/uas/oauth/requestToken'
    access_token_url = 'https://api.linkedin.com/uas/oauth/accessToken'
    authorize_url = 'https://www.linkedin.com/uas/oauth/authenticate'

    def complete_login(self, request, app, token, response):
        client = LinkedInAPI(request, app.client_id, app.secret,
                             self.request_token_url)
        extra_data = client.get_user_info()
        return self.sociallogin_from_response(request, extra_data)

    def get_default_scope(self):
        scope = []
        if app_settings.QUERY_EMAIL:
            scope.append('r_emailaddress')
        return scope

    def get_profile_fields(self):
        default_fields = ['id',
                          'first-name',
                          'last-name',
                          'email-address',
                          'picture-url',
                          'picture-urls::(original)',
                          # picture-urls::(original) is higher res
                          'public-profile-url']
        fields = self.get_settings().get('PROFILE_FIELDS', default_fields)
        return fields

    def extract_uid(self, data):
        return data['id']

    def extract_common_fields(self, data):
        return dict(email=data.get('email-address'),
                    first_name=data.get('first-name'),
                    last_name=data.get('last-name'))


provider_classes = [LinkedInProvider]
