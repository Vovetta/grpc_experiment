from os import environ
from time import time

from grpc import server, ServerInterceptor
from concurrent import futures
from prometheus_client import start_http_server
from python_grpc_prometheus.prometheus_server_interceptor import _wrap_rpc_behavior
from python_grpc_prometheus.server_metrics import SERVER_HANDLED_LATENCY_SECONDS
from python_grpc_prometheus.util import split_call_details, type_from_method

from service_pb2 import (
    GreetingsRequest, GreetingsResponse,
    MultiplyRequest, MultiplyResponse,
    FibonacciRequest, FibonacciResponse
)
from service_pb2_grpc import ServiceServicer, add_ServiceServicer_to_server


SERVER_PORT = environ.get('PYTHON_SERVER_PORT', '50051')
METRICS_PORT = int(environ.get('PYTHON_SERVER_METRICS_PORT', '1111'))


class ServiceLatencyInterceptor(ServerInterceptor):

    def intercept_service(self, continuation, handler_call_details):

        grpc_service, grpc_method, ok = split_call_details(handler_call_details)
        if not ok:
            return continuation(handler_call_details)

        def latency_wrapper(behavior, request_streaming, response_streaming):
            grpc_type = type_from_method(request_streaming, response_streaming)

            def new_behavior(request_or_iterator, service_context):
                start = time()
                try:
                    return behavior(request_or_iterator, service_context)
                finally:
                    SERVER_HANDLED_LATENCY_SECONDS.labels(
                        grpc_type=grpc_type,
                        grpc_service=grpc_service,
                        grpc_method=grpc_method).observe(max(time() - start, 0))

            return new_behavior

        return _wrap_rpc_behavior(continuation(handler_call_details), latency_wrapper)


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
        result = 0
        for request in request_iterator:
            result = request.number * request.multiplier
        return MultiplyResponse(result=result)

    def MultiplyStreamStream(self, request_iterator: MultiplyRequest, context):
        for request in request_iterator:
            yield MultiplyResponse(result=request.number * request.multiplier)

    def FibonacciUnaryUnary(self, request: FibonacciRequest, context):
        return FibonacciResponse(result=fibonacci(request.number))

    def FibonacciUnaryStream(self, request: FibonacciRequest, context):
        yield FibonacciResponse(result=fibonacci(request.number))

    def FibonacciStreamUnary(self, request_iterator: FibonacciRequest, context):
        result = 0
        for request in request_iterator:
            result = fibonacci(request.number)
        return FibonacciResponse(result=result)

    def FibonacciStreamStream(self, request_iterator: FibonacciRequest, context):
        for request in request_iterator:
            yield FibonacciResponse(result=fibonacci(request.number))


def serve():
    service = server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=[ServiceLatencyInterceptor()]
    )
    add_ServiceServicer_to_server(Service(), service)
    service.add_insecure_port(f'[::]:{SERVER_PORT}')
    service.start()

    print(f'Server running at http://127.0.0.1:{SERVER_PORT}')
    print(f'Metrics running at http://127.0.0.1:{METRICS_PORT}')

    service.wait_for_termination()


if __name__ == '__main__':
    start_http_server(METRICS_PORT)
    serve()
