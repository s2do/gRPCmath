from nmath.cli.main import build_parser


def test_ping_defaults():
    parser = build_parser()

    args = parser.parse_args(["ping"])

    assert args.command == "ping"
    assert args.message == "hello"
    assert args.server == "127.0.0.1:50051"


def test_ping_arguments():
    parser = build_parser()

    args = parser.parse_args(
        [
            "ping",
            "--message",
            "test",
            "--server",
            "127.0.0.1:50052",
        ]
    )

    assert args.command == "ping"
    assert args.message == "test"
    assert args.server == "127.0.0.1:50052"