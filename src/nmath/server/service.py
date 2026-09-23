from nmath.generated import math_pb2, math_pb2_grpc


class MathService(math_pb2_grpc.MathServiceServicer):
    """Implementation of the nmath gRPC service."""

    def Ping(
        self,
        request: math_pb2.PingRequest,
        context,
    ) -> math_pb2.PingResponse:
        return math_pb2.PingResponse(
            message=f"pong: {request.message}",
        )