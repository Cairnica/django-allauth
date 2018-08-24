import importlib

from collections import OrderedDict

from django.conf import settings
from django.utils.functional import cached_property

from allauth.utils import import_attribute

from .base import Provider


class ProviderRegistry(object):
    def __init__(self):
        self._provider_map = OrderedDict()

    @cached_property
    def provider_map(self):
        for provider in settings.PROVIDERS:
            try:
                provider_class = import_attribute(provider)
            except (ImportError, AttributeError):
                provider_module = importlib.import_module(provider + '.provider')
                # TODO Find the class

            self.register(provider_class)

        return self._provider_map

    def register(self, factory, id=None, **kwargs):
        if not isinstance(factory, Provider.Factory):
            factory = factory.Factory(factory, id, **kwargs)
        elif id or kwargs:
            raise ValueError(f'Cannot provide id or kwargs when registering an instanciated Factory')
        self._provider_map[factory.id] = factory

    def get_list(self):
        return list(self.provider_map.values())

    def by_id(self, id):
        return self.provider_map[id]

    def as_choices(self):
        for provider_cls in self.provider_map.values():
            yield (provider_cls.id, provider_cls.name)

registry = ProviderRegistry()
