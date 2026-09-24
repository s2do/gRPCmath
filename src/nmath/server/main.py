from concurrent import futures

import grpc

from nmath.config import NMATH_HOST, NMATH_PORT
from nmath.generated import math_pb2_grpc
from nmath.server.service import MathService


DEFAULT_HOST = NMATH_HOST
DEFAULT_PORT = NMATH_PORT


def create_server(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
) -> tuple[grpc.Server, int]:
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
    )

    math_pb2_grpc.add_MathServiceServicer_to_server(
        MathService(),
        server,
    )

    bound_port = server.add_insecure_port(
        f"{host}:{port}",
    )

    if bound_port == 0:
        raise RuntimeError(
            f"Could not bind gRPC server to {host}:{port}"
        )

    return server, bound_port


def serve(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
) -> None:
    server, bound_port = create_server(host, port)

    server.start()

    print(f"nmath server listening on {host}:{bound_port}")

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("stopping nmath server")
        server.stop(grace=0)


def main() -> None:
    serve()


if __name__ == "__main__":
    main()