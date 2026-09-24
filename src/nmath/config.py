import os

from dotenv import load_dotenv


load_dotenv()

DEFAULT_SOCKET = "/tmp/nmath.sock"

NMATH_SOCKET = os.getenv(
    "NMATH_SOCKET",
    DEFAULT_SOCKET,
)