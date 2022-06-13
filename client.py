import grpc.experimental

protos = grpc.protos('service.proto')
services = grpc.services('service.proto')

response = services.Service.GreetingsUnaryUnary(
    protos.GreetingsRequest(name='you'),
    'localhost:50051',
    insecure=True
)
print('Message: ' + response.message)

response = services.Service.GreetingsUnaryStream(
    protos.GreetingsRequest(name='you'),
    'localhost:50051',
    insecure=True
)
print('Message: ' + ', '.join(res.message for res in response))

response = services.Service.GreetingsStreamUnary(
    iter([protos.GreetingsRequest(name='Hi'), protos.GreetingsRequest(name='you')]),
    'localhost:50051',
    insecure=True
)
print('Message: ' + response.message)

response = services.Service.GreetingsStreamStream(
    iter([protos.GreetingsRequest(name='Hi'), protos.GreetingsRequest(name='you')]),
    'localhost:50051',
    insecure=True
)
print('Message: ' + ', '.join(res.message for res in response))
