from .AdvancedTimer import AdvancedTimer

from typing import Any


class NamedSingletonMeta(type):
    _named_instances: dict[str, Any] = {}
    
    def __call__(cls, name: str = None, *args, **kwargs):
        if name is None:
            return super().__call__(name, *args, **kwargs)
        if name in cls._named_instances:
            return cls._named_instances[name]
        
        instance = super().__call__(name, *args, **kwargs)
        cls._named_instances[name] = instance
        return instance


class GlobalTimer(AdvancedTimer, metaclass=NamedSingletonMeta):
    @classmethod
    def get_timers(cls):
        return cls._named_instances.copy()
