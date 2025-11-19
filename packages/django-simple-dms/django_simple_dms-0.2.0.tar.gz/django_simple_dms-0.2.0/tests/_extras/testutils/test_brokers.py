import typing
from decimal import Decimal as D  # noqa: N817


if typing.TYPE_CHECKING:
    from datetime import date


class BadBroker:
    def get_rates(self, day: 'date', symbols: list[str] = None) -> dict[str, D]:
        raise NotImplementedError('_dummy_')


class DummyBroker:
    def get_rates(self, day: 'date', symbols: list[str] = None) -> dict[str, D]:
        return {'_base': 'AAA', 'AAA': D(1), 'BBB': D(2), 'EUR': D(3), '_provider': 'testutils.bad_broker.DummyBroker'}
