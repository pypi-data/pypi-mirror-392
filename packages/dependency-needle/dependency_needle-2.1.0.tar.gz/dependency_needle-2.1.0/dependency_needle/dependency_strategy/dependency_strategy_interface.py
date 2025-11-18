from abc import ABC, abstractmethod
from typing import Dict, Hashable, Optional, Type, Union

from dependency_needle.constants import ANNOTATIONS, RETURN, INIT
from dependency_needle.constants.constants import InterfaceType


class IDependencyStrategyInterface(ABC):
    """Dependency strategy interface to customize building
    and cleaning implementation."""

    def __init__(
            self,
            interface_lifetime_registery_lookup: Union[
                Dict[Type[InterfaceType], InterfaceType],
                Dict[Hashable, Dict[Type[InterfaceType], InterfaceType]]
            ],
            interface: Type[InterfaceType],
            concrete_class: Type[InterfaceType]
    ):
        self._interface_lifetime_registery_lookup\
            = interface_lifetime_registery_lookup
        self.__interface = interface
        self._concrete_class = concrete_class

    def __gaurd_build_unregistered_interface(
        self,
        interface: Type[InterfaceType],
        registery_lookup: Dict[Type[InterfaceType],
                               'IDependencyStrategyInterface']
    ):
        """Throw 'KeyError' exception if interface is not registered."""
        if interface not in registery_lookup:
            raise KeyError(f"Interface: {interface} is not registered.")

    @abstractmethod
    def _custom_pre_build_strategy(
            self,
            interface: Type[InterfaceType],
            key_lookup: Hashable
    ) -> Optional[InterfaceType]:
        """Method to override in order to customize pre creation behavior."""
        pass

    @abstractmethod
    def _custom_post_build_strategy(
            self,
            interface: Type[InterfaceType],
            concrete_class_instance: InterfaceType,
            key_lookup: Hashable
    ) -> None:
        """Method to override in order to customize post creation behavior."""
        pass

    def _build(
        self,
        interface: Type[InterfaceType],
        interface_registery: Dict[Type[InterfaceType],
                                  'IDependencyStrategyInterface'],
        key_lookup: Hashable
    ) -> InterfaceType:
        """Actual building method, used recursively.

        :param interface: interface required to be built.
        :param interface_registery: registery containing interface key\
              and DependencyStrategy objects values.
        :param key_lookup: key_lookup that\
            might be used to store in the lookup.
        """
        self.__gaurd_build_unregistered_interface(
            interface, interface_registery)  # type: ignore

        concrete_class = self._custom_pre_build_strategy(
            interface, key_lookup)

        if not concrete_class:
            created_dependencies = {}
            class_registered: IDependencyStrategyInterface = (
                interface_registery[interface]
            )
            class_to_build = class_registered._concrete_class

            if hasattr(getattr(class_to_build, INIT), ANNOTATIONS):
                dependencies: Dict[type, type] = getattr(
                    getattr(class_to_build, INIT), ANNOTATIONS)

                if RETURN in dependencies:
                    dependencies.pop(RETURN)

                for key, value in dependencies.items():
                    dependency_registered: IDependencyStrategyInterface = (
                        interface_registery[value]
                    )
                    created_dependencies[key] = dependency_registered.build(
                        interface,
                        interface_registery,
                        key_lookup
                    )

            concrete_class = class_to_build(**created_dependencies)

        self._custom_post_build_strategy(
            interface, concrete_class, key_lookup)

        return concrete_class  # type: ignore

    def build(
        self,
        interface_type: Type[InterfaceType],
        interface_registery: Dict[Type[InterfaceType],
                                  'IDependencyStrategyInterface'],
        key_lookup: Hashable
    ) -> InterfaceType:
        """Build an interface by going through the dependency lookup.

        :param interface: interface required to be built.
        :param key_lookup: key_lookup that\
            might be used to store in the lookup.
        """
        return self._build(self.__interface,
                           interface_registery, key_lookup)  # type: ignore
