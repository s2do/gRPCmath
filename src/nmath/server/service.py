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
    
    def BinaryOperation(
        self,
        request: math_pb2.BinaryOperationRequest,
        context,
    ) -> math_pb2.BinaryOperationResponse:
        left = request.left_operand
        right = request.right_operand
        op = request.operator

        try:
            if op == math_pb2.OPERATOR_ADD:
                res = np.add(left, right)
            elif op == math_pb2.OPERATOR_SUB:
                res = np.subtract(left, right)
            elif op == math_pb2.OPERATOR_MUL:
                res = np.multiply(left, right)
            elif op == math_pb2.OPERATOR_DIV:
                if right == 0:
                    return math_pb2.BinaryOperationResponse(
                        result=0.0,
                        status=math_pb2.STATUS_DIV_BY_ZERO,
                    )
                res = np.divide(left, right)
            else:
                return math_pb2.BinaryOperationResponse(
                    result=0.0,
                    status=math_pb2.STATUS_ERROR,
                )

            if np.isnan(res):
                return math_pb2.BinaryOperationResponse(
                    result=0.0,
                    status=math_pb2.STATUS_NAN,
                )

            return math_pb2.BinaryOperationResponse(
                result=float(res),
                status=math_pb2.STATUS_SUCCESS,
            )
        except Exception:
            return math_pb2.BinaryOperationResponse(
                result=0.0,
                status=math_pb2.STATUS_ERROR,
            )