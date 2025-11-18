from dependency_injector.wiring import Provide
from kong.common.timed import Timed
from kong.proto.service_pb2 import Response
from kong.proto.service_pb2_grpc import GrpcBindingServicer
from kong.sdk.container import Container
from kong.sdk.kong_function_instance import KongFunctionInstance
from kong.session.session_context import session_context


class GrpcBinding(GrpcBindingServicer):
    def __init__(self, fn: KongFunctionInstance = Provide[Container.fn]):
        super().__init__()
        self.__fn = fn.get()

    @Timed(
        value="kong_sdk_function",
        extra_tags=["method", "call", "package", "kong-sdk-python"],
        percentiles=(0.5, 0.75, 0.9, 0.95, 0.99),
    )
    async def call(self, request, context):
        with session_context(request.session):
            result = await self.__fn.call(
                request.input,
                request.session.deadline.ToDatetime(),
            )

            return Response(output=result.json())
