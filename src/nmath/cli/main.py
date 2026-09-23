import argparse

from nmath.client.service import MathClient


DEFAULT_SERVER = "127.0.0.1:50051"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nmath",
        description="nmath mathematical execution engine",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    ping_parser = subparsers.add_parser(
        "ping",
        help="test connectivity to the nmath server",
    )

    ping_parser.add_argument(
        "--message",
        default="hello",
        help="message sent to the server",
    )

    ping_parser.add_argument(
        "--server",
        default=DEFAULT_SERVER,
        help=f"gRPC server address (default: {DEFAULT_SERVER})",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "ping":
        client = MathClient(args.server)

        try:
            response = client.ping(args.message)
            print(response)
        finally:
            client.close()