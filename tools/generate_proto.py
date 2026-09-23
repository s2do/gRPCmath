from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PROTO_DIR = ROOT / "proto"
OUTPUT_DIR = ROOT / "src" / "nmath" / "generated"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    command = [
        sys.executable,
        "-m",
        "grpc_tools.protoc",
        "-I",
        str(PROTO_DIR),
        "--python_out",
        str(OUTPUT_DIR),
        "--pyi_out",
        str(OUTPUT_DIR),
        "--grpc_python_out",
        str(OUTPUT_DIR),
        str(PROTO_DIR / "math.proto"),
    ]

    subprocess.run(command, check=True)

    grpc_file = OUTPUT_DIR / "math_pb2_grpc.py"
    content = grpc_file.read_text(encoding="utf-8")

    content = re.sub(
        r"^import (math_pb2) as math__pb2$",
        r"from . import \1 as math__pb2",
        content,
        flags=re.MULTILINE,
    )

    grpc_file.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()