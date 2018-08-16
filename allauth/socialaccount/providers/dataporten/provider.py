import requests

from allauth.socialaccount.providers.base import ProviderAccount, ProviderException
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class DataportenAccount(ProviderAccount):
    def get_avatar_url(self):
        '''
        Returns a valid URL to an 128x128 .png photo of the user
        '''
        # Documentation for user profile photos can be found here:
        # https://docs.dataporten.no/docs/oauth-authentication/
        base_url = 'https://api.dataporten.no/userinfo/v1/user/media/'
        return base_url + self.account.extra_data['profilephoto']

    def to_str(self):
        '''
        Returns string representation of a social account. Includes the name
        of the user.
        '''
        dflt = super(DataportenAccount, self).to_str()
        return '%s (%s)' % (
            self.account.extra_data.get('name', ''),
            dflt,
        )


class DataportenProvider(OAuth2Provider):
    id = 'dataporten'
    name = 'Dataporten'
    account_class = DataportenAccount

    access_token_url = 'https://auth.dataporten.no/oauth/token'
    authorize_url = 'https://auth.dataporten.no/oauth/authorization'
    profile_url = 'https://auth.dataporten.no/userinfo'
    groups_url = 'https://groups-api.dataporten.no/groups/'

    def extract_uid(self, data):
        '''
        Returns the primary user identifier, an UUID string
        See: https://docs.dataporten.no/docs/userid/
        '''
        return data['userid']

    def extract_extra_data(self, data):
        '''
        Extracts fields from `data` that will be stored in
        `SocialAccount`'s `extra_data` JSONField.

        All the necessary data extraction has already been done in the
        complete_login()-view, so we can just return the data.
        PS: This is default behaviour, so we did not really need to define
            this function, but it is included for documentation purposes.

        Typical return dict:
        {
            "userid": "76a7a061-3c55-430d-8ee0-6f82ec42501f",
            "userid_sec": ["feide:andreas@uninett.no"],
            "name": "Andreas \u00c5kre Solberg",
            "email": "andreas.solberg@uninett.no",
            "profilephoto": "p:a3019954-902f-45a3-b4ee-bca7b48ab507",
        }
        '''
        return data

    def extract_common_fields(self, data):
        '''
        This function extracts information from the /userinfo endpoint which
        will be consumed by allauth.socialaccount.adapter.populate_user().
        Look there to find which key-value pairs that should be saved in the
        returned dict.

        Typical return dict:
        {
            "userid": "76a7a061-3c55-430d-8ee0-6f82ec42501f",
            "userid_sec": ["feide:andreas@uninett.no"],
            "name": "Andreas \u00c5kre Solberg",
            "email": "andreas.solberg@uninett.no",
            "profilephoto": "p:a3019954-902f-45a3-b4ee-bca7b48ab507",
            "username": "andreas",
        }
        '''
        # Make shallow copy to prevent possible mutability issues
        data = dict(data)

        # If a Feide username is available, use it. If not, use the "username"
        # of the email-address
        for userid in data.get('userid_sec'):
            usertype, username = userid.split(':')
            if usertype == 'feide':
                data['username'] = username.split('@')[0]
                break
        else:
            # Only entered if break is not executed above
            data['username'] = data.get('email').split('@')[0]

        return data

    def complete_login(self, request, app, token, **kwargs):
        '''
        Arguments:
            request - The get request to the callback URL
                        /accounts/dataporten/login/callback.
            app - The corresponding SocialApp model instance
            token - A token object with access token given in token.token
        Returns:
            Should return a dict with user information intended for parsing
            by the methods of the DataportenProvider view, i.e.
            extract_uid(), extract_extra_data(), and extract_common_fields()
        '''
        # The athentication header
        headers = {'Authorization': 'Bearer ' + token.token}

        # Userinfo endpoint, for documentation see:
        # https://docs.dataporten.no/docs/oauth-authentication/
        userinfo_response = requests.get(
            self.get_profile_url(request),
            headers=headers,
        )
        # Raise exception for 4xx and 5xx response codes
        userinfo_response.raise_for_status()

        # The endpoint returns json-data and it needs to be decoded
        extra_data = userinfo_response.json()['user']

        # Finally test that the audience property matches the client id
        # for validification reasons, as instructed by the Dataporten docs
        # if the userinfo-response is used for authentication
        if userinfo_response.json()['audience'] != app.client_id:
            raise ProviderException(
                'Dataporten returned a user with an audience field \
                 which does not correspond to the client id of the \
                 application.'
            )

        return self.sociallogin_from_response(
            request,
            extra_data,
        )


provider_classes = [DataportenProvider]
