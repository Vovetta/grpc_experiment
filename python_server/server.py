from os import environ

from grpc import server
from concurrent import futures
from py_grpc_prometheus.prometheus_server_interceptor import PromServerInterceptor
from prometheus_client import start_http_server

from service_pb2 import GreetingsResponse, GreetingsRequest
from service_pb2_grpc import ServiceServicer, add_ServiceServicer_to_server


SERVER_PORT = environ.get('PYTHON_SERVER_PORT', '50051')
METRICS_PORT = int(environ.get('PYTHON_SERVER_METRICS_PORT', '1111'))


class Service(ServiceServicer):
    def GreetingsUnaryUnary(self, request: GreetingsRequest, context):
        return GreetingsResponse(message=request.name)

    def GreetingsUnaryStream(self, request: GreetingsRequest, context):
        yield GreetingsResponse(message=request.name)

    def GreetingsStreamUnary(self, request_iterator: GreetingsRequest, context):
        message = []
        for request in request_iterator:
            message.append(request.name)
        return GreetingsResponse(message=', '.join(message))

    def GreetingsStreamStream(self, request_iterator: GreetingsRequest, context):
        for request in request_iterator:
            yield GreetingsResponse(message=request.name)


def serve():
    service = server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=[PromServerInterceptor(enable_handling_time_histogram=True)]
    )
    add_ServiceServicer_to_server(Service(), service)
    service.add_insecure_port(f'[::]:{SERVER_PORT}')
    service.start()
    service.wait_for_termination()


if __name__ == '__main__':
    start_http_server(METRICS_PORT)
    serve()
