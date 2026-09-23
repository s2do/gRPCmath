from nmath.client.service import MathClient
from nmath.generated import math_pb2


class FakeMathServiceStub:
    def __init__(self):
        self.requests = []

    def Ping(self, request):
        self.requests.append(request)

        return math_pb2.PingResponse(
            message=f"pong: {request.message}",
        )


def test_ping_sends_expected_request(monkeypatch):
    client = MathClient("unused:50051")

    fake_stub = FakeMathServiceStub()
    monkeypatch.setattr(client, "_stub", fake_stub)

    response = client.ping("hello")

    assert response == "pong: hello"
    assert len(fake_stub.requests) == 1
    assert fake_stub.requests[0].message == "hello"


def test_close_closes_channel(monkeypatch):
    client = MathClient("unused:50051")

    closed = False

    def fake_close():
        nonlocal closed
        closed = True

    monkeypatch.setattr(client._channel, "close", fake_close)

    client.close()

    assert closed