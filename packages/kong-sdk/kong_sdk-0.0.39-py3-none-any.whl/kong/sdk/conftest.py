from collections.abc import Callable
from typing import TypeAlias

import pytest
from pydantic import BaseModel

from kong.sdk.container import Container
from kong.sdk.kong_function import KongFunction

ExtensionFixture: TypeAlias = Callable[
    [type[KongFunction], type[BaseModel]], KongFunction
]


@pytest.fixture
def create_extension() -> ExtensionFixture:
    def wrapper(
        kong_function_class: type[KongFunction], input_data_class: type[BaseModel]
    ):
        di = Container()
        di.fn().set(
            kong_function_class(
                class_of_input_data=input_data_class,
            )
        )
        return di.fn().get()

    return wrapper
