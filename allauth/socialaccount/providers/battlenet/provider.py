import requests

from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.providers.oauth2.client import OAuth2Error


class BattleNetAccount(ProviderAccount):
    def to_str(self):
        battletag = self.account.extra_data.get("battletag")
        return battletag or super(BattleNetAccount, self).to_str()


class Region:
    APAC = "apac"
    CN = "cn"
    EU = "eu"
    KR = "kr"
    SEA = "sea"
    TW = "tw"
    US = "us"


def _check_errors(response):
    try:
        data = response.json()
    except ValueError:  # JSONDecodeError on py3
        raise OAuth2Error(
            "Invalid JSON from Battle.net API: %r" % (response.text)
        )

    if response.status_code >= 400 or "error" in data:
        # For errors, we expect the following format:
        # {"error": "error_name", "error_description": "Oops!"}
        # For example, if the token is not valid, we will get:
        # {
        #   "error": "invalid_token",
        #   "error_description": "Invalid access token: abcdef123456"
        # }
        # For the profile API, this may also look like the following:
        # {"code": 403, "type": "Forbidden", "detail": "Account Inactive"}
        error = data.get("error", "") or data.get("type", "")
        desc = data.get("error_description", "") or data.get("detail", "")

        raise OAuth2Error("Battle.net error: %s (%s)" % (error, desc))

    # The expected output from the API follows this format:
    # {"id": 12345, "battletag": "Example#12345"}
    # The battletag is optional.
    if "id" not in data:
        # If the id is not present, the output is not usable (no UID)
        raise OAuth2Error("Invalid data from Battle.net API: %r" % (data))

    return data


class BattleNetProvider(OAuth2Provider):
    """
    OAuth2 adapter for Battle.net
    https://dev.battle.net/docs/read/oauth

    Region is set to us by default, but can be overridden with the
    `region` GET parameter when performing a login.
    Can be any of eu, us, kr, sea, tw or cn
    """

    id = "battlenet"
    name = "Battle.net"
    account_class = BattleNetAccount
    
    valid_regions = (
        Region.APAC,
        Region.CN,
        Region.EU,
        Region.KR,
        Region.SEA,
        Region.TW,
        Region.US,
    )

    def extract_uid(self, data):
        uid = str(data["id"])
        if data.get("region") == "cn":
            # China is on a different account system. UIDs can clash with US.
            return uid + "-cn"
        return uid

    def extract_common_fields(self, data):
        return {"username": data.get("battletag")}

    def get_default_scope(self):
        # Optional scopes: "sc2.profile", "wow.profile"
        return []

    def get_region(self, request):
        region = request.GET.get("region", "").lower()
        if region == Region.SEA:
            # South-East Asia uses the same region as US everywhere
            return Region.US
        if region in self.valid_regions:
            return region
        return Region.US

    def get_access_token_url(self, request):
        region = self.get_region(request)
        if region == Region.CN:
            return "https://www.battlenet.com.cn/oauth/token"
        return "https://%s.battle.net/oauth/token" % (region)

    def get_authorize_url(self, request):
        region = self.get_region(request)
        if region == Region.CN:
            return "https://www.battlenet.com.cn/oauth/token"
        return "https://%s.battle.net/oauth/token" % (region)

    def get_profile_url(self, request):
        if self.get_region(request) == "cn":
            return "https://api.battlenet.com.cn/account/user"
        return "https://%s.api.battle.net/account/user" % (self.get_region(request))

    def complete_login(self, request, app, token, **kwargs):
        params = {"access_token": token.token}
        response = requests.get(self.get_profile_url(request), params=params)
        data = _check_errors(response)

        # Add the region to the data so that we can have it in `extra_data`.
        data["region"] = self.get_region(request)

        return self.sociallogin_from_response(request, data)

    def get_callback_url(self, request, app):
        r = super().get_callback_url(request, app)
        region = request.GET.get("region", "").lower()
        # Pass the region down to the callback URL if we specified it
        if region and region in self.valid_regions:
            r += "?region=%s" % (region)
        return r


provider_classes = [BattleNetProvider]
