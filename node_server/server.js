const http = require("http");
const url = require("url");
const grpc = require("@grpc/grpc-js");
const protoLoader = require('@grpc/proto-loader');
require('dotenv').config();

const serverProxy = require('./interceptors');
const { grpcMetricsMiddleware, client } = require('./middleware')();

const SERVER_PORT = process.env.NODE_SERVER_PORT ?? '50052'
const METRICS_PORT = process.env.NODE_SERVER_METRICS_PORT ?? '1112'
const grpcBind = `localhost:${SERVER_PORT}`;

const packageDefinition = protoLoader.loadSync('service.proto', {});
const service = grpc.loadPackageDefinition(packageDefinition).service;

const createServer = () => {
    const server = serverProxy(new grpc.Server());
    server.use(grpcMetricsMiddleware);
    server
        .addService(service.Service.service, {
            GreetingsUnaryUnary: async (call, callback) => {
                const request = call.request;
                callback(null, {message: request.name});
            },
            GreetingsUnaryStream: async (call) => {
                const request = call.request;
                call.write({message: request.name});
                call.end();
            },
            GreetingsStreamUnary: async (call, callback) => {
                let message = '';
                for await (let data of call) {
                    if (message) message += ', ';
                    message += data.name;
                }
                callback(null, {message: message});
            },
            GreetingsStreamStream: async (call, callback) => {
                call.on('data', function(data) {
                    call.write({message: data.name});
                });
                call.on('end', function() {
                    call.end();
                });
            },
            MultiplyUnaryUnary: async (call) => {
                const request = new GreetingsRequest(call.request);
                return new GreetingsResponse({message: `Hello, ${request.name}!`});
            },
            MultiplyUnaryStream: async (call) => {
                const request = new GreetingsRequest(call.request);
                return new GreetingsResponse({message: `Hello, ${request.name}!`});
            },
            MultiplyStreamUnary: async (call) => {
                const request = new GreetingsRequest(call.request);
                return new GreetingsResponse({message: `Hello, ${request.name}!`});
            },
            MultiplyStreamStream: async (call) => {
                const request = new GreetingsRequest(call.request);
                return new GreetingsResponse({message: `Hello, ${request.name}!`});
            },
            FibonacciUnaryUnary: async (call) => {
                const request = new GreetingsRequest(call.request);
                return new GreetingsResponse({message: `Hello, ${request.name}!`});
            },
            FibonacciUnaryStream: async (call) => {
                const request = new GreetingsRequest(call.request);
                return new GreetingsResponse({message: `Hello, ${request.name}!`});
            },
            FibonacciStreamUnary: async (call) => {
                const request = new GreetingsRequest(call.request);
                return new GreetingsResponse({message: `Hello, ${request.name}!`});
            },
            FibonacciStreamStream: async (call) => {
                const request = new GreetingsRequest(call.request);
                return new GreetingsResponse({message: `Hello, ${request.name}!`});
            },
        })
    server.bindAsync(
        grpcBind,
        grpc.ServerCredentials.createInsecure(),
        (error, port) => {
            if (error) {
                throw new Error(error);
            }

            console.log(`Server running at http://127.0.0.1:${SERVER_PORT}`);
            console.log(`Metrics running at http://127.0.0.1:${METRICS_PORT}`);
            server.start();
        }
    );
}

createServer()

const server = http.createServer(async (req, res) => {
  // Retrieve route from request object
  const route = url.parse(req.url).pathname

  if (route === '/metrics') {
    // Return all metrics the Prometheus exposition format
    res.setHeader('Content-Type', client.register.contentType)
    res.end(client.register.metrics())
  }
})

server.listen(METRICS_PORT)
