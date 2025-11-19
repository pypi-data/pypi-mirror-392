import typing
from functools import lru_cache
from typing import TypedDict

from django.utils.translation import gettext as _
from django_xchange.exceptions import ConfigurationError
from django_xchange.types import BrokerType


class ConfigType(TypedDict):
    BASE_CURRENCY: str
    CURRENCIES: list[str]
    BROKERS: list[BrokerType]


class Config:
    def __init__(self) -> None:
        from django.conf import settings  # noqa: PLC0415

        Config._conf = getattr(settings, 'DJANGO_XCHANGE', {})
        if not Config._conf.get('BROKERS'):
            raise ConfigurationError(_('No brokers configured'))

    def __getattr__(self, item: str) -> object:
        if item in Config._conf:
            item = Config._conf.get(item)
            if callable(item):
                return item()
            return item
        raise AttributeError(item)


@lru_cache(maxsize=1)
def get_config() -> ConfigType:
    return typing.cast('ConfigType', Config())


def get_base_currency() -> str:
    return get_config().BASE_CURRENCY
