import grpc.experimental

protos = grpc.protos('service.proto')
services = grpc.services('service.proto')

response = services.Service.GreetingsUnaryUnary(
    protos.GreetingsRequest(name='you'),
    'localhost:50051',
    insecure=True
)
print(f'Message: {response.message}')

response = services.Service.GreetingsUnaryStream(
    protos.GreetingsRequest(name='you'),
    'localhost:50051',
    insecure=True
)
print(f'Message: {", ".join(res.message for res in response)}')

response = services.Service.GreetingsStreamUnary(
    iter([protos.GreetingsRequest(name='Hi'), protos.GreetingsRequest(name='you')]),
    'localhost:50051',
    insecure=True
)
print(f'Message: {response.message}')

response = services.Service.GreetingsStreamStream(
    iter([protos.GreetingsRequest(name='Hi'), protos.GreetingsRequest(name='you')]),
    'localhost:50051',
    insecure=True
)
print(f'Message: {", ".join(res.message for res in response)}')

response = services.Service.MultiplyUnaryUnary(
    protos.MultiplyRequest(number=5, multiplier=15),
    'localhost:50051',
    insecure=True
)
print(f'Message: {response.result}')

response = services.Service.MultiplyUnaryStream(
    protos.MultiplyRequest(number=5, multiplier=15),
    'localhost:50051',
    insecure=True
)
print(f'Message: {", ".join(str(res.result) for res in response)}')

response = services.Service.MultiplyStreamUnary(
    iter([protos.MultiplyRequest(number=5, multiplier=15), protos.MultiplyRequest(number=8, multiplier=13)]),
    'localhost:50051',
    insecure=True
)
print(f'Message: {response.result}')

response = services.Service.MultiplyStreamStream(
    iter([protos.MultiplyRequest(number=5, multiplier=15), protos.MultiplyRequest(number=8, multiplier=13)]),
    'localhost:50051',
    insecure=True
)
print(f'Message: {", ".join(str(res.result) for res in response)}')

response = services.Service.FibonacciUnaryUnary(
    protos.FibonacciRequest(number=50),
    'localhost:50051',
    insecure=True
)
print(f'Message: {response.result}')

response = services.Service.FibonacciUnaryStream(
    protos.FibonacciRequest(number=80),
    'localhost:50051',
    insecure=True
)
print(f'Message: {", ".join(str(res.result) for res in response)}')

response = services.Service.FibonacciStreamUnary(
    iter([protos.FibonacciRequest(number=80), protos.FibonacciRequest(number=50)]),
    'localhost:50051',
    insecure=True
)
print(f'Message: {response.result}')

response = services.Service.FibonacciStreamStream(
    iter([protos.FibonacciRequest(number=90), protos.FibonacciRequest(number=15)]),
    'localhost:50051',
    insecure=True
)
print(f'Message: {", ".join(str(res.result) for res in response)}')
