import argparse
import os
import socket
import threading

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

        # Temporary M1 plumbing.
        #
        # Replace this with:
        #
        # response = client.binary_operation(expression)
        #
        # once BinaryOperation exists in the gRPC API.
        response = client.ping(expression)

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
) -> None:
    if os.path.exists(socket_path):
        os.unlink(socket_path)

    server_client = MathClient(server_address)

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
                args=(connection, server_client),
                daemon=True,
            )

            thread.start()

    except KeyboardInterrupt:
        print("stopping nmath bridge")
    finally:
        server_client.close()
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


if __name__ == "__main__":import argparse
import os
import socket
import threading

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

        # Temporary M1 plumbing.
        #
        # Replace this with:
        #
        # response = client.binary_operation(expression)
        #
        # once BinaryOperation exists in the gRPC API.
        response = client.ping(expression)

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