from nmath.generated import math_pb2
from nmath.server.service import MathService


def test_ping_returns_pong_message():
    service = MathService()

    request = math_pb2.PingRequest(message="hello")

    response = service.Ping(request, None)

    assert isinstance(response, math_pb2.PingResponse)
    assert response.message == "pong: hello"


def test_ping_preserves_empty_message():
    service = MathService()

    request = math_pb2.PingRequest(message="")

    response = service.Ping(request, None)

    assert response.message == "pong: "