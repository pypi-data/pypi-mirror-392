import grpc
from kong.proto import healthcheck_pb2
from kong.proto.healthcheck_pb2_grpc import HealthStub

channel = grpc.insecure_channel("localhost:8701")
stub = HealthStub(channel)
request = healthcheck_pb2.HealthCheckRequest(service="")
response_future = stub.Check.future(request)
print(response_future.result())
