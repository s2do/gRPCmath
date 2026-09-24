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

    def binary_operation(self, left: float, right: float, operator: str) -> str:
        op_map = {
            "+": math_pb2.OPERATOR_ADD,
            "-": math_pb2.OPERATOR_SUB,
            "*": math_pb2.OPERATOR_MUL,
            "/": math_pb2.OPERATOR_DIV,
        }

        if operator not in op_map:
            return f"error: unsupported operator '{operator}'"

        request = math_pb2.BinaryOperationRequest(
            left_operand=left,
            right_operand=right,
            operator=op_map[operator],
        )

        try:
            response = self._stub.BinaryOperation(request)

            if response.status == math_pb2.STATUS_SUCCESS:
                # Format to remove trailing .0 for clean integer outputs
                return f"{response.result:g}"
            elif response.status == math_pb2.STATUS_DIV_BY_ZERO:
                return "error: division by zero"
            elif response.status == math_pb2.STATUS_NAN:
                return "error: not a number (NaN)"
            else:
                return "error: unknown calculation error"

        except grpc.RpcError as exc:
            return f"grpc error: {exc.details()}"

    def close(self) -> None:
        self._channel.close()