from abc import ABC, abstractmethod
from typing import Never


class Importer(ABC):
    @abstractmethod
    def import_file(self, file_path: str, *args, **kwargs) -> Never:
        """To be implemented."""
        raise NotImplementedError()
