import importlib
import inspect

from collections import OrderedDict

from django.conf import settings
from django.utils.functional import cached_property

from allauth.utils import import_attribute


class ProviderRegistry(object):
    def __init__(self):
        self._provider_map = OrderedDict()

    @cached_property
    def provider_map(self):
        for provider in settings.PROVIDERS:
            self.register_settings(provider)

        return self._provider_map

    def register_settings(self, provider):
        if isinstance(provider, str):
            provider_path = provider
            provider = {}
        elif isinstance(provider, dict):
            provider = provider.copy()
            provider_path = provider.pop('class')

        provider_class = None
        
        try:
            provider_module = importlib.import_module(provider_path + '.provider')
        except ImportError:
            try:
                provider_class = import_attribute(provider_path)
            except (ImportError, AttributeError):
                provider_module = importlib.import_module(provider_path)
            else:
                if inspect.ismodule(provider_class):
                    provider_module = provider_class
                    provider_class = None

        if provider_class is None:
            if hasattr(provider_module, 'provider_classes'):
                provider_classes = provider_module.provider_classes
            else:
                from .base import Provider
                provider_classes = [
                    # obj for name, obj in inspect.getmembers(provider_module)
                    # if inspect.isclass(obj) and issubclass(obj, Provider)
                ]

            if len(provider_classes) > 1:
                raise ValueError(f"Too many Provider Types in {provider_path}")

            if not provider_classes:
                raise ValueError(f"No provider type in {provider_path}")


            provider_class = provider_classes[0]

        return self.register(provider_class, **provider)

    def register(self, factory, **kwargs):
        from .base import Provider
        
        if not isinstance(factory, Provider.Factory):
            factory = factory.Factory(factory, **kwargs)
        elif id or kwargs:
            raise ValueError(f'Cannot provide id or kwargs when registering an instanciated Factory')
        if factory.id in self._provider_map:
            raise ValueError(f'Attempt to register two providers with id "{factory.id}" ()')
        self._provider_map[factory.id] = factory

    def unregister(self, id):
        del self.provider_map[id]

    def get_list(self):
        return list(self.provider_map.values())

    def get_provider_list(self, request):
        return [pf.create_provider(request) for pf in self.get_list()]

    def by_id(self, id):
        return self.provider_map[id]

    def as_choices(self):
        for provider_cls in self.provider_map.values():
            yield (provider_cls.id, provider_cls.name)

registry = ProviderRegistry()
