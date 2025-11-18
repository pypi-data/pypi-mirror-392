from concurrent import futures

import grpc
from grpc_health.v1 import health
from grpc_health.v1 import health_pb2_grpc


def setup_health_check(server: grpc.Server):
    health_servicer = health.HealthServicer(
        experimental_non_blocking=True,
        experimental_thread_pool=futures.ThreadPoolExecutor(max_workers=10),
    )
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
