from typing import Dict, Hashable, Optional, Type
from threading import Lock

from dependency_needle.constants.constants import InterfaceType
from dependency_needle.dependency_strategy.\
    dependency_strategy_interface import IDependencyStrategyInterface


singleton_build_lock_lookup = {}
lookup_lock = Lock()


class SingeltonDependencyStrategy(IDependencyStrategyInterface):
    """Scoped strategy for dependency building."""

    def _custom_pre_build_strategy(
        self,
        interface: Type[InterfaceType],
        key_lookup: Hashable
    ) -> Optional[InterfaceType]:
        """Singelton pre build strategy"""
        if (
            interface
            in self._interface_lifetime_registery_lookup
        ):
            return (
                (self._interface_lifetime_registery_lookup
                 [interface])  # type: ignore
            )
        return None

    def _custom_post_build_strategy(
        self,
        interface: Type[InterfaceType],
        concrete_class_instance: InterfaceType,
        key_lookup: Hashable
    ) -> None:
        """Singelton post build strategy"""
        if (
            interface not
            in self._interface_lifetime_registery_lookup
        ):
            (self._interface_lifetime_registery_lookup
             [interface]) = concrete_class_instance  # type: ignore

    def _build(
        self,
        interface: Type[InterfaceType],
        interface_registery: Dict[Type[InterfaceType],
                                  IDependencyStrategyInterface],
        key_lookup: Hashable
    ) -> InterfaceType:
        with lookup_lock:
            if interface not in singleton_build_lock_lookup:
                singleton_build_lock_lookup[interface] = Lock()
        with singleton_build_lock_lookup[interface]:
            built_interface = super()._build(interface,
                                             interface_registery,
                                             key_lookup)
        with lookup_lock:
            singleton_build_lock_lookup.pop(interface)
        return built_interface
