from dependency_injector import containers, providers

from kong.sdk.config import SdkConfig
from kong.sdk.kong_function_instance import KongFunctionInstance


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    sdk_config = providers.Singleton(SdkConfig)

    wiring_config = containers.WiringConfiguration(
        modules=["kong.sdk.use_state", "kong.sdk.grpc_binding"],
    )

    fn = providers.Singleton(KongFunctionInstance)
