from typing import Hashable, Optional, Type
from dependency_needle.constants.constants import InterfaceType
from dependency_needle.dependency_strategy.\
    dependency_strategy_interface import IDependencyStrategyInterface


class TransientDependencyStrategy(IDependencyStrategyInterface):
    """Transient strategy for dependency building."""

    def _custom_pre_build_strategy(
            self,
            interface: Type[InterfaceType],
            key_lookup: Hashable
    ) -> Optional[InterfaceType]:
        """Method to override in order to customize pre creation behavior."""
        pass

    def _custom_post_build_strategy(
            self,
            interface: Type[InterfaceType],
            concrete_class_instance: InterfaceType,
            key_lookup: Hashable
    ) -> None:
        """Method to override in order to customize post creation behavior."""
        pass
