from logging import basicConfig

from grpc import server
from concurrent import futures
from py_grpc_prometheus.prometheus_server_interceptor import PromServerInterceptor
from prometheus_client import start_http_server

from service_pb2 import GreetingsResponse, GreetingsRequest
from service_pb2_grpc import ServiceServicer, add_ServiceServicer_to_server


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
        interceptors=[PromServerInterceptor()]
    )
    add_ServiceServicer_to_server(Service(), service)
    service.add_insecure_port('[::]:50051')
    service.start()
    service.wait_for_termination()


# Start an end point to expose metrics.
start_http_server(1111)

if __name__ == '__main__':
    basicConfig()
    serve()
