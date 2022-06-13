from os import environ

from grpc import server
from concurrent import futures
from py_grpc_prometheus.prometheus_server_interceptor import PromServerInterceptor
from prometheus_client import start_http_server

from service_pb2 import (
    GreetingsRequest, GreetingsResponse,
    MultiplyRequest, MultiplyResponse,
    FibonacciRequest, FibonacciResponse
)
from service_pb2_grpc import ServiceServicer, add_ServiceServicer_to_server


SERVER_PORT = environ.get('PYTHON_SERVER_PORT', '50051')
METRICS_PORT = int(environ.get('PYTHON_SERVER_METRICS_PORT', '1111'))


def fibonacci(n):
    if not (isinstance(n, int) and n >= 0):
        raise ValueError(f'Positive integer number expected, got "{n}"')

    if n in {0, 1}:
        return n

    previous, fib_number = 0, 1
    for _ in range(2, n + 1):
        previous, fib_number = fib_number, previous + fib_number

    return fib_number


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

    def MultiplyUnaryUnary(self, request: MultiplyRequest, context):
        return MultiplyResponse(result=request.number * request.multiplier)

    def MultiplyUnaryStream(self, request: MultiplyRequest, context):
        yield MultiplyResponse(result=request.number * request.multiplier)

    def MultiplyStreamUnary(self, request_iterator: MultiplyRequest, context):
        message = []
        for request in request_iterator:
            message.append(request.number * request.multiplier)
        return MultiplyResponse(result=message[-1])

    def MultiplyStreamStream(self, request_iterator: MultiplyRequest, context):
        for request in request_iterator:
            yield MultiplyResponse(result=request.number * request.multiplier)

    def FibonacciUnaryUnary(self, request: FibonacciRequest, context):
        return FibonacciResponse(result=fibonacci(request.number))

    def FibonacciUnaryStream(self, request: FibonacciRequest, context):
        yield FibonacciResponse(result=fibonacci(request.number))

    def FibonacciStreamUnary(self, request_iterator: FibonacciRequest, context):
        message = []
        for request in request_iterator:
            message.append(fibonacci(request.number))
        return FibonacciResponse(result=message[-1])

    def FibonacciStreamStream(self, request_iterator: FibonacciRequest, context):
        for request in request_iterator:
            yield FibonacciResponse(result=fibonacci(request.number))


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
