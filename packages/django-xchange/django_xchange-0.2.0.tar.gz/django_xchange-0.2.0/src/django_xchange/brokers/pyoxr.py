import os
from decimal import Decimal

from pyoxr import OXRClient, init
from django_xchange.brokers.common import BrokerProtocol
import typing


if typing.TYPE_CHECKING:
    from datetime import date


class PyoxrBroker(BrokerProtocol):
    _initialised = False

    def __init__(self, **kwargs) -> None:
        if not PyoxrBroker._initialised:
            init(os.environ.get('OPEN_EXCHANGE_RATES_APP_ID'))
            PyoxrBroker._initialised = True

    def get_rates(self, day: 'date', symbols: list[str]) -> dict[str, typing.Any]:
        client = OXRClient.default_api
        res = client.get_historical(date=day.strftime('%Y-%m-%d'), symbols=','.join(sorted(symbols)))
        return {
            '_base': res['base'],
            '_provider': 'django_xchange.brokers.pyoxr.PyoxrBroker',
        } | {k: Decimal(str(v)) for k, v in res['rates'].items()}
