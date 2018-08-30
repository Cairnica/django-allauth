SECRET_KEY = 'psst'
SITE_ID = 1

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

ROOT_URLCONF = 'allauth.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'
            ],
        },
    },
]

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

PROVIDERS = [
    # 'allauth.socialaccount.providers.common.amazon',
    # 'allauth.socialaccount.providers.common.auth0',
    # 'allauth.socialaccount.providers.common.authentiq',
    # 'allauth.socialaccount.providers.common.dropbox',
    # 'allauth.socialaccount.providers.common.evernote',
    # 'allauth.socialaccount.providers.common.feedly',
    # 'allauth.socialaccount.providers.common.foursquare',
    # 'allauth.socialaccount.providers.common.google',
    # 'allauth.socialaccount.providers.common.linkedin_oauth2',
    # 'allauth.socialaccount.providers.common.linkedin',
    # 'allauth.socialaccount.providers.common.microsoft',
    # 'allauth.socialaccount.providers.common.twitter',
    # 'allauth.socialaccount.providers.common.yahoo',

    # 'allauth.socialaccount.providers.communication.discord',
    # 'allauth.socialaccount.providers.communication.disqus',
    # 'allauth.socialaccount.providers.communication.reddit',
    # 'allauth.socialaccount.providers.communication.salesforce',
    # 'allauth.socialaccount.providers.communication.slack',
    # 'allauth.socialaccount.providers.communication.telegram',
    # 'allauth.socialaccount.providers.communication.trello',
    # 'allauth.socialaccount.providers.communication.tumblr',
    # 'allauth.socialaccount.providers.communication.windowslive',


    # 'allauth.socialaccount.providers.dev_sites.asana',
    # 'allauth.socialaccount.providers.dev_sites.azure',
    # 'allauth.socialaccount.providers.dev_sites.bitbucket_oauth2',
    # 'allauth.socialaccount.providers.dev_sites.bitbucket',
    # 'allauth.socialaccount.providers.dev_sites.digitalocean',
    # 'allauth.socialaccount.providers.dev_sites.fxa',
    # 'allauth.socialaccount.providers.dev_sites.github',
    # 'allauth.socialaccount.providers.dev_sites.gitlab',
    # 'allauth.socialaccount.providers.dev_sites.mailchimp',
    # 'allauth.socialaccount.providers.dev_sites.mailru',
    # 'allauth.socialaccount.providers.dev_sites.stackexchange',

    # 'allauth.socialaccount.providers.financial.patreon',
    # 'allauth.socialaccount.providers.financial.paypal',
    # 'allauth.socialaccount.providers.financial.quickbooks',
    # 'allauth.socialaccount.providers.financial.shopify',
    # 'allauth.socialaccount.providers.financial.stripe',

    # 'allauth.socialaccount.providers.media.eveonline',
    # 'allauth.socialaccount.providers.media.fivehundredpx',
    # 'allauth.socialaccount.providers.media.flickr',
    # 'allauth.socialaccount.providers.media.instagram',
    # 'allauth.socialaccount.providers.media.pinterest',
    # 'allauth.socialaccount.providers.media.soundcloud',
    # 'allauth.socialaccount.providers.media.spotify',
    # 'allauth.socialaccount.providers.media.twitch',
    # 'allauth.socialaccount.providers.media.vimeo',

    # 'allauth.socialaccount.providers.other.agave',
    # 'allauth.socialaccount.providers.other.angellist',
    # 'allauth.socialaccount.providers.other.baidu',
    # 'allauth.socialaccount.providers.other.basecamp',
    # 'allauth.socialaccount.providers.other.battlenet',
    # 'allauth.socialaccount.providers.other.bitly',
    # 'allauth.socialaccount.providers.other.box',
    # 'allauth.socialaccount.providers.other.cern',
    # 'allauth.socialaccount.providers.other.coinbase',
    # 'allauth.socialaccount.providers.other.dataporten',
    # 'allauth.socialaccount.providers.other.daum',
    # 'allauth.socialaccount.providers.other.douban',
    # 'allauth.socialaccount.providers.other.doximity',
    # 'allauth.socialaccount.providers.other.draugiem',
    # 'allauth.socialaccount.providers.other.dwolla',
    # 'allauth.socialaccount.providers.other.edmodo',
    # 'allauth.socialaccount.providers.other.eventbrite',
    # 'allauth.socialaccount.providers.other.globus',
    # 'allauth.socialaccount.providers.other.hubic',
    # 'allauth.socialaccount.providers.other.kakao',
    # 'allauth.socialaccount.providers.other.line',
    # 'allauth.socialaccount.providers.other.meetup',
    # 'allauth.socialaccount.providers.other.naver',
    # 'allauth.socialaccount.providers.other.odnoklassniki',
    # 'allauth.socialaccount.providers.other.orcid',
    # 'allauth.socialaccount.providers.other.robinhood',
    # 'allauth.socialaccount.providers.other.twentythreeandme',
    # 'allauth.socialaccount.providers.other.untappd',
    # 'allauth.socialaccount.providers.other.vk',
    # 'allauth.socialaccount.providers.other.weibo',
    # 'allauth.socialaccount.providers.other.weixin',
    # 'allauth.socialaccount.providers.other.xing',
]

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    'allauth.socialaccount.providers.core.openid',
    'allauth.socialaccount.providers.core.persona',
    'allauth.socialaccount.providers.common.facebook',
)

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

STATIC_ROOT = '/tmp/'  # Dummy
STATIC_URL = '/static/'
