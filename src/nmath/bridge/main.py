import argparse
import os
import re
import socket
import threading
import grpc

from nmath.client.service import MathClient
from nmath.config import NMATH_SOCKET

DEFAULT_SERVER = "127.0.0.1:50051"

def handle_client(
    connection: socket.socket,
    client: MathClient,
) -> None:
    try:
        data = connection.recv(4096)

        if not data:
            return

        expression = data.decode("utf-8").strip()

        if not expression:
            connection.sendall(b"error: empty expression\n")
            return

        # Parse the expression: (left number) (operator) (right number)
        pattern = r"^\s*([-+]?\d*\.?\d+)\s*([+\-*/])\s*([-+]?\d*\.?\d+)\s*$"
        match = re.match(pattern, expression)

        if not match:
            # Fallback: Treat invalid math as a diagnostic ping to check server health
            try:
                ping_response = client.ping(expression)
                error_msg = f"error: unknown expression. Server is reachable ({ping_response})"
            except grpc.RpcError as rpc_exc:
                # Catch the specific 'server down' unavailability state
                if rpc_exc.code() == grpc.StatusCode.UNAVAILABLE:
                    error_msg = "error: unknown expression. (Note: The nmath bridge is running, but the backend gRPC server is offline)."
                else:
                    error_msg = f"error: unknown expression. (gRPC error: {rpc_exc.details()})"
            except Exception as exc:
                error_msg = f"error: unknown expression. (Unexpected error: {exc})"
            
            connection.sendall(f"{error_msg}\n".encode("utf-8"))
            return

        left_op = float(match.group(1))
        operator = match.group(2)
        right_op = float(match.group(3))

        # Call the new gRPC binary_operation method
        response = client.binary_operation(left_op, right_op, operator)

        connection.sendall(
            f"{response}\n".encode("utf-8"),
        )
    except Exception as exc:
        connection.sendall(
            f"error: {exc}\n".encode("utf-8"),
        )
    finally:
        connection.close()

def serve(
    socket_path: str,
    server_address: str,
    client: MathClient | None = None,
) -> None:
    if os.path.exists(socket_path):
        os.unlink(socket_path)

    if client is None:
        client = MathClient(server_address)

    server_socket = socket.socket(
        socket.AF_UNIX,
        socket.SOCK_STREAM,
    )

    server_socket.bind(socket_path)
    server_socket.listen()

    print(f"nmath bridge listening on {socket_path}")

    try:
        while True:
            connection, _ = server_socket.accept()

            thread = threading.Thread(
                target=handle_client,
                args=(connection, client),
                daemon=True,
            )
            thread.start()

    except KeyboardInterrupt:
        print("stopping nmath bridge")

    finally:
        client.close()
        server_socket.close()

        if os.path.exists(socket_path):
            os.unlink(socket_path)

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nmath-bridge",
        description="nmath Unix socket bridge",
    )

    parser.add_argument(
        "--socket",
        default=NMATH_SOCKET,
        help=(
            f"Unix socket path "
            f"(default: {NMATH_SOCKET})"
        ),
    )

    parser.add_argument(
        "--server",
        default=DEFAULT_SERVER,
        help=(
            f"gRPC server address "
            f"(default: {DEFAULT_SERVER})"
        ),
    )

    return parser

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    serve(
        socket_path=args.socket,
        server_address=args.server,
    )

if __name__ == "__main__":
    main()