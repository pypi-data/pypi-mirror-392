from abc import ABC, abstractmethod
from typing import Hashable, Type

from dependency_needle.constants import InterfaceType


class IContainer(ABC):

    @abstractmethod
    def build(
        self,
        interface: Type[InterfaceType],
        key_lookup: Hashable
    ) -> InterfaceType:
        """Build an interface by utilizing the registery lookup.

        :param interface: interface needed to be built
        :param key_lookup: key_lookup that might be used to lookup\
        registered interfaces.
        :return object: concrete class that implemenets that interface
        """
        pass
