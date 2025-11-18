from abc import ABC, abstractmethod
from asyncio import run
from typing import Hashable

from dependency_needle.container import Container, IContainer
from dependency_needle.lifetime_enums import LifeTimeEnums


async def main():
    class MockInterfaceOne(ABC):
        """Mock interface class."""
        @abstractmethod
        def mock_method(self):
            """Mock interface method."""
            pass

    class MockInterfaceTwo(ABC):
        """Mock interface class."""

        @abstractmethod
        def mock_method(self):
            """Mock interface method."""
            pass

    class MockInterfaceThree(ABC):
        """Mock interface class."""

        @abstractmethod
        def mock_method(self):
            """Mock interface method."""
            pass

    class ConcreteOne(MockInterfaceOne):
        def mock_method(self):
            pass

    class ConcreteTwo(MockInterfaceTwo):
        def __init__(self, dependency_one: MockInterfaceOne):
            pass

        def mock_method(self):
            pass

    class ConcreteThree(MockInterfaceThree):
        def __init__(self, dependency_one: MockInterfaceOne,
                     dependency_two: MockInterfaceTwo):
            pass

        def mock_method(self):
            pass

    container = Container()

    container.register_interface(
        MockInterfaceOne, ConcreteOne, LifeTimeEnums.SINGLETON)
    container.register_interface(
        MockInterfaceTwo, ConcreteTwo, LifeTimeEnums.SCOPED)
    container.register_interface(
        MockInterfaceThree, ConcreteThree, LifeTimeEnums.TRANSIENT)

    @container.build_dependencies_decorator(id_kwarg='request')
    def method_with_dependencies_kwarg(
            request: Hashable,
            dependency: MockInterfaceThree) -> MockInterfaceThree:
        return dependency

    @container.build_dependencies_decorator(id_arg=1)
    async def method_with_dependencies_arg(
            request: Hashable,
            dependency: IContainer) -> MockInterfaceThree:
        lazy_built_dep = dependency.build(MockInterfaceThree, request)
        return lazy_built_dep

    HASHABLE_LOOKUP = 'MockLookUp'

    dependency_array = [
        # Mocking an invocation of a decorated method.
        method_with_dependencies_kwarg(request=HASHABLE_LOOKUP),
        # Mocking an invocation of a decorated async method.
        await method_with_dependencies_arg(HASHABLE_LOOKUP),
        # Manual build of dependency.
        container.build(MockInterfaceThree, HASHABLE_LOOKUP)
    ]

    return dependency_array

if True:
    # Prints out an array of built classes.
    output = run(main())
    print(output)
