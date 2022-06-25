const http = require("http");
const url = require("url");
const grpc = require("@grpc/grpc-js");
const protoLoader = require('@grpc/proto-loader');
require('dotenv').config();

const serverProxy = require('./interceptors');
const { grpcMetricsMiddleware, client } = require('./middleware')();

const SERVER_PORT = process.env.NODE_SERVER_PORT ?? '50052'
const METRICS_PORT = process.env.NODE_SERVER_METRICS_PORT ?? '1112'
const grpcBind = `0.0.0.0:${SERVER_PORT}`;

const packageDefinition = protoLoader.loadSync('./service.proto', {});
const service = grpc.loadPackageDefinition(packageDefinition).service;

function fibonacci(n){
  let arr = [0, 1];
  for (let i = 2; i < n + 1; i++){
    arr.push(arr[i - 2] + arr[i -1])
  }
 return arr[n]
}

const createServer = () => {
    const server = serverProxy(new grpc.Server());
    server.use(grpcMetricsMiddleware);
    server
        .addService(service.Service.service, {
            GreetingsUnaryUnary: async (call, callback) => {
                callback(null, {message: call.request.name});
            },
            GreetingsUnaryStream: async (call) => {
                call.write({message: call.request.name});
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
            GreetingsStreamStream: async (call) => {
                call.on('data', function(data) {
                    call.write({message: data.name});
                });
                call.on('end', function() {
                    call.end();
                });
            },
            MultiplyUnaryUnary: async (call, callback) => {
                callback(null, {result: call.request.number * call.request.multiplier});
            },
            MultiplyUnaryStream: async (call) => {
                call.write({result: call.request.number * call.request.multiplier});
                call.end();
            },
            MultiplyStreamUnary: async (call, callback) => {
                let result = 0;
                for await (let data of call) {
                    result = data.number * data.multiplier
                }
                callback(null, {result: result});
            },
            MultiplyStreamStream: async (call) => {
                call.on('data', function(data) {
                    call.write({result: data.number * data.multiplier});
                });
                call.on('end', function() {
                    call.end();
                });
            },
            FibonacciUnaryUnary: async (call, callback) => {
                callback(null, {result: fibonacci(call.request.number)});
            },
            FibonacciUnaryStream: async (call) => {
                call.write({result: fibonacci(call.request.number)});
                call.end();
            },
            FibonacciStreamUnary: async (call, callback) => {
                let result = 0;
                for await (let data of call) {
                    result = fibonacci(data.number)
                }
                callback(null, {result: result});
            },
            FibonacciStreamStream: async (call) => {
                call.on('data', function(data) {
                    call.write({result: fibonacci(data.number)});
                });
                call.on('end', function() {
                    call.end();
                });
            }
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
  const route = url.parse(req.url).pathname

  if (route === '/metrics') {
    res.setHeader('Content-Type', client.register.contentType)
    res.end(client.register.metrics())
  }
})

server.listen(METRICS_PORT)
