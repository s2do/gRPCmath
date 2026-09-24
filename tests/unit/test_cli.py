import io

from nmath.cli.main import build_parser, main


def test_expression_argument():
    parser = build_parser()

    args = parser.parse_args(["1+2"])

    assert args.expression == "1+2"


def test_socket_argument():
    parser = build_parser()

    args = parser.parse_args(
        [
            "--socket",
            "/tmp/test-nmath.sock",
            "1+2",
        ]
    )

    assert args.expression == "1+2"
    assert args.socket == "/tmp/test-nmath.sock"


def test_expression_can_be_read_from_stdin(monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.stdin",
        io.StringIO("1-2\n"),
    )

    monkeypatch.setattr(
        "nmath.cli.main.send_expression",
        lambda socket_path, expression: expression,
    )

    main([])

    captured = capsys.readouterr()

    assert captured.out.strip() == "1-2"