import grpc

from nmath.generated import math_pb2, math_pb2_grpc


class MathClient:
    """Client for the nmath gRPC service."""

    def __init__(self, address: str):
        self._channel = grpc.insecure_channel(address)
        self._stub = math_pb2_grpc.MathServiceStub(self._channel)

    def ping(self, message: str) -> str:
        response = self._stub.Ping(
            math_pb2.PingRequest(message=message),
        )

        return response.message

    def close(self) -> None:
        self._channel.close()