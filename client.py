import logging

import grpc
import grpc.experimental
from prometheus_client import start_http_server

from py_grpc_prometheus.prometheus_client_interceptor import PromClientInterceptor

# NOTE: The path to the .proto file must be reachable from an entry
# on sys.path. Use sys.path.insert or set the $PYTHONPATH variable to
# import from files located elsewhere on the filesystem.

protos = grpc.protos("service.proto")
services = grpc.services("service.proto")

logging.basicConfig()

channel = grpc.intercept_channel(grpc.insecure_channel('localhost:50051'), PromClientInterceptor())

start_http_server(1112)

response = services.Service.GreetingsUnaryUnary(
    protos.GreetingsRequest(name='you'),
    'localhost:50051',
    insecure=True
)
print("Message: " + response.message)

response = services.Service.GreetingsUnaryStream(
    protos.GreetingsRequest(name='you'),
    'localhost:50051',
    insecure=True
)
print("Message: " + ', '.join(res.message for res in response))

response = services.Service.GreetingsStreamUnary(
    iter([protos.GreetingsRequest(name='Hi'), protos.GreetingsRequest(name='you')]),
    'localhost:50051',
    insecure=True
)
print("Message: " + response.message)

response = services.Service.GreetingsStreamStream(
    iter([protos.GreetingsRequest(name='Hi'), protos.GreetingsRequest(name='you')]),
    'localhost:50051',
    insecure=True
)
print("Message: " + ', '.join(res.message for res in response))
