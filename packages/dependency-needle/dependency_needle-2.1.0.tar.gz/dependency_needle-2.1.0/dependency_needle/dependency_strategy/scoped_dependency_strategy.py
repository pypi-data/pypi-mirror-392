from typing import Hashable, Optional, Type
from dependency_needle.constants.constants import InterfaceType
from dependency_needle.dependency_strategy.\
    dependency_strategy_interface import IDependencyStrategyInterface


class ScopedDependencyStrategy(IDependencyStrategyInterface):
    """Scoped strategy for dependency building."""

    def _custom_pre_build_strategy(
        self,
        interface: Type[InterfaceType],
        key_lookup: Hashable
    ) -> Optional[InterfaceType]:
        """Scoped pre build strategy"""
        if (
            key_lookup in self._interface_lifetime_registery_lookup and
            interface in (self._interface_lifetime_registery_lookup
                          [key_lookup])  # type: ignore
        ):
            return (
                (self._interface_lifetime_registery_lookup
                 [key_lookup])[interface]  # type: ignore

            )
        return None

    def _custom_post_build_strategy(
        self,
        interface: Type[InterfaceType],
        concrete_class_instance: InterfaceType,
        key_lookup: Hashable
    ) -> None:
        """Scoped post build strategy"""

        if (key_lookup not
                in self._interface_lifetime_registery_lookup):
            (self._interface_lifetime_registery_lookup
             [key_lookup]) = {  # type: ignore
                interface: concrete_class_instance
            }
        elif (
            interface not
            in (self._interface_lifetime_registery_lookup
                [key_lookup])  # type: ignore
        ):
            (self._interface_lifetime_registery_lookup
             [key_lookup]).update(  # type: ignore
                {
                    interface: concrete_class_instance  # type: ignore
                }
            )
