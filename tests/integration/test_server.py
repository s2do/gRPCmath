from concurrent import futures

import grpc

from nmath.generated import math_pb2, math_pb2_grpc
from nmath.server.main import create_server
from nmath.server.service import MathService


def test_ping_service():
    service = MathService()

    request = math_pb2.PingRequest(message="hello")
    response = service.Ping(request, None)

    assert response.message == "pong: hello"


def test_ping_over_grpc():
    server, port = create_server(port=0)
    server.start()

    try:
        with grpc.insecure_channel(f"127.0.0.1:{port}") as channel:
            stub = math_pb2_grpc.MathServiceStub(channel)

            response = stub.Ping(
                math_pb2.PingRequest(message="hello")
            )

            assert response.message == "pong: hello"
    finally:
        server.stop(grace=0)