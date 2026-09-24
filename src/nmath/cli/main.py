import argparse
import socket
import sys

from nmath.config import NMATH_SOCKET


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nmath",
        description="nmath mathematical expression client",
    )

    parser.add_argument(
        "expression",
        nargs="?",
        help='mathematical expression, e.g. "1+2"',
    )

    parser.add_argument(
        "--socket",
        default=NMATH_SOCKET,
        help=(
            f"Unix socket path "
            f"(default: {NMATH_SOCKET})"
        ),
    )

    return parser


def send_expression(
    socket_path: str,
    expression: str,
) -> str:
    try:
        with socket.socket(
            socket.AF_UNIX,
            socket.SOCK_STREAM,
        ) as client_socket:
            client_socket.connect(socket_path)

            client_socket.sendall(
                f"{expression}\n".encode("utf-8"),
            )

            response = client_socket.recv(4096)

        return response.decode("utf-8").rstrip("\n")
    except FileNotFoundError:
        return f"error: nmath bridge is not running (socket file '{socket_path}' missing)."
    except ConnectionRefusedError:
        return f"error: nmath bridge is not responding at '{socket_path}'."
    except Exception as exc:
        return f"error: failed to communicate with bridge ({exc})"


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    expression = args.expression

    if expression is None:
        expression = sys.stdin.read().strip()

    if not expression:
        parser.error("no expression supplied")

    response = send_expression(
        socket_path=args.socket,
        expression=expression,
    )

    print(response)


if __name__ == "__main__":
    main()