import typing
from abc import abstractmethod
from decimal import Decimal

if typing.TYPE_CHECKING:
    from datetime import date


@typing.runtime_checkable
class BrokerProtocol(typing.Protocol):
    @abstractmethod
    def get_rates(self, day: 'date', symbols: list[str]) -> dict[str, Decimal]:
        raise NotImplementedError()


type BrokerType = str | BrokerProtocol
