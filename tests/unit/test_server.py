import math
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

def test_binary_operation_addition():
    service = MathService()
    request = math_pb2.BinaryOperationRequest(
        left_operand=3.0,
        right_operand=2.0,
        operator=math_pb2.OPERATOR_ADD,
    )
    response = service.BinaryOperation(request, None)

    assert response.status == math_pb2.STATUS_SUCCESS
    assert response.result == 5.0


def test_binary_operation_division_by_zero():
    service = MathService()
    request = math_pb2.BinaryOperationRequest(
        left_operand=10.0,
        right_operand=0.0,
        operator=math_pb2.OPERATOR_DIV,
    )
    response = service.BinaryOperation(request, None)

    assert response.status == math_pb2.STATUS_DIV_BY_ZERO


def test_binary_operation_invalid_operator():
    service = MathService()
    request = math_pb2.BinaryOperationRequest(
        left_operand=10.0,
        right_operand=2.0,
        operator=math_pb2.OPERATOR_UNSPECIFIED,
    )
    response = service.BinaryOperation(request, None)

    assert response.status == math_pb2.STATUS_ERROR