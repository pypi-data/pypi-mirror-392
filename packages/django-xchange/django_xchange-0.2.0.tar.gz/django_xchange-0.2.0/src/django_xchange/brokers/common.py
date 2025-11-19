import typing
from decimal import Decimal
from gettext import gettext as _

from django_xchange.types import BrokerProtocol
from django_xchange.utils import resolve_fqn
from django_xchange.exceptions import ConfigurationError

if typing.TYPE_CHECKING:
    from datetime import date


class BrokerManager:
    def get_rates(self, day: 'date', symbols: list[str] = None) -> dict[str, Decimal]:
        from django_xchange.config import get_config, get_base_currency

        if not (brokers := get_config().BROKERS):
            raise ConfigurationError(_('No brokers configured'))
        for broker in brokers:
            try:
                if isinstance(broker, BrokerProtocol):
                    resolved = broker()
                else:
                    resolved = resolve_fqn(broker)()
                rates = resolved.get_rates(day, symbols)
                base = get_base_currency()
                if base != rates['_base']:
                    ratio = round(Decimal(1 / rates[base]), 8)
                    new_rates = {k: float(round(v * ratio, 6)) for k, v in rates.items() if not k.startswith('_')}
                    rates |= new_rates | {'_base': base}
                return rates
            except Exception:  # noqa: BLE001, S110
                # TODO: think of better handling
                pass
        raise RuntimeError(_('No rates available'))
