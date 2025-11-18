from kong.sdk.kong_function import KongFunction


class KongFunctionInstance:
    def __init__(self):
        self.__instance: type[KongFunction] = None  # type: ignore

    def get(self) -> type[KongFunction]:
        if self.__instance is None:
            raise ValueError("KongFunction instance has not been created")
        return self.__instance

    def set(self, value: type[KongFunction]):
        self.__instance = value
