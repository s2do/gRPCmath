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

    def BinaryOperation(self, request):
        self.requests.append(request)
        
        if request.operator == math_pb2.OPERATOR_ADD:
            return math_pb2.BinaryOperationResponse(
                result=request.left_operand + request.right_operand,
                status=math_pb2.STATUS_SUCCESS,
            )
        elif request.operator == math_pb2.OPERATOR_DIV and request.right_operand == 0:
            return math_pb2.BinaryOperationResponse(
                result=0.0,
                status=math_pb2.STATUS_DIV_BY_ZERO,
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

def test_binary_operation_sends_expected_request(monkeypatch):
    client = MathClient("unused:50051")
    fake_stub = FakeMathServiceStub()
    monkeypatch.setattr(client, "_stub", fake_stub)

    response = client.binary_operation(3.0, 2.0, "+")

    assert response == "5"
    assert len(fake_stub.requests) == 1
    assert fake_stub.requests[0].left_operand == 3.0
    assert fake_stub.requests[0].operator == math_pb2.OPERATOR_ADD


def test_binary_operation_division_by_zero(monkeypatch):
    client = MathClient("unused:50051")
    monkeypatch.setattr(client, "_stub", FakeMathServiceStub())

    response = client.binary_operation(10.0, 0.0, "/")

    assert response == "error: division by zero"