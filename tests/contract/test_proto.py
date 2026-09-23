from nmath.generated import math_pb2, math_pb2_grpc


def test_ping_messages_exist():
    request = math_pb2.PingRequest(message="hello")
    response = math_pb2.PingResponse(message="world")

    assert request.message == "hello"
    assert response.message == "world"


def test_ping_messages_round_trip():
    request = math_pb2.PingRequest(message="hello")

    serialized = request.SerializeToString()
    restored = math_pb2.PingRequest.FromString(serialized)

    assert restored.message == "hello"


def test_math_service_stub_exists():
    assert hasattr(math_pb2_grpc, "MathServiceStub")


def test_math_service_servicer_exists():
    assert hasattr(math_pb2_grpc, "MathServiceServicer")