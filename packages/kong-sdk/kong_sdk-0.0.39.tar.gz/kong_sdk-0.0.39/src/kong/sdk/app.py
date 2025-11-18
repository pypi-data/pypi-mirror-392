import asyncio
import importlib.metadata
import json
import multiprocessing
import platform
import socket
from concurrent import futures
from contextlib import contextmanager

import grpc
from grpc_health.v1 import health_pb2
from grpc_reflection.v1alpha import reflection
from kong.common.app_logger import app_logger
from kong.proto import service_pb2
from kong.proto.service_pb2_grpc import add_GrpcBindingServicer_to_server
from kong.sdk.container import Container
from kong.sdk.grpc_binding import GrpcBinding
from kong.sdk.health_check import setup_health_check
from kong.sdk.kong_function import KongFunction
from pydantic import BaseModel

logger = app_logger(__name__)


class App:
    def __init__(
        self,
        input_data_class: type[BaseModel],
        output_data_class: type[BaseModel],
        kong_function_class: type[KongFunction],
    ):
        logger.info(
            "init function",
            lambda: dict(version=importlib.metadata.version("kong_sdk")),
        )

        self.__input_type = input_data_class
        self.__output_type = output_data_class
        self.__di = Container()
        self.__di.fn().set(
            kong_function_class(
                class_of_input_data=input_data_class,
            )
        )

    async def __create_server(self, address):
        logger.info("start server", lambda: dict(address=address))

        settings = self.__di.sdk_config()

        server = grpc.aio.server(
            futures.ThreadPoolExecutor(
                max_workers=settings.app.workers,
            ),
            options=(("grpc.so_reuseport", 1),),
        )
        add_GrpcBindingServicer_to_server(GrpcBinding(), server)
        setup_health_check(server)

        service_names = (
            service_pb2.DESCRIPTOR.services_by_name["GrpcBinding"].full_name,
            health_pb2.DESCRIPTOR.services_by_name["Health"].full_name,
            reflection.SERVICE_NAME,
        )
        reflection.enable_server_reflection(service_names, server)

        server.add_insecure_port(address)
        await server.start()
        logger.info(
            "have start server result",
            lambda: dict(
                status="ready",
                address=address,
                services=service_names,
            ),
        )

        await server.wait_for_termination()

    def run(self, argv):
        if "--schema" in argv:
            self.print_model()
            return

        @contextmanager
        def bind_port(port: int):
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            if sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT) == 0:
                raise IOError(f"Failed to set socket.SOL_SOCKET for port {port}")

            sock.bind(("", port))

            try:
                yield sock.getsockname()[1]
            finally:
                sock.close()

        settings = self.__di.sdk_config()
        address = f"{settings.app.host}:{settings.app.port}"

        # Windows doesn't support socket.SO_REUSEPORT
        if platform.system() == "Windows":
            asyncio.run(self.__create_server(address))
        else:
            logger.info(
                "create workers",
                lambda: dict(count=settings.app.workers, port=settings.app.port),
            )
            with bind_port(settings.app.port):
                workers = []
                for _ in range(settings.app.workers):
                    worker = multiprocessing.Process(
                        target=asyncio.run,
                        args=(self.__create_server(address),),
                    )
                    worker.start()
                    workers.append(worker)

                for worker in workers:
                    worker.join()

    def print_model(self):
        schema = dict(
            input=self.__input_type.model_json_schema(),
            output=self.__output_type.model_json_schema(),
        )
        print(json.dumps(schema, indent=2))
