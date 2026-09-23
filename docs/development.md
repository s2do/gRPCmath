# Development

## Environment

Create a virtual environment:

    python3 -m venv .venv
    source .venv/bin/activate

Install development dependencies:

    pip install -e ".[dev]"

## Running tests

Run all tests:

    pytest

Run with coverage:

    pytest --cov=nmath --cov-report=term-missing

Run a specific test category:

    pytest tests/unit
    pytest tests/integration
    pytest tests/contract
    pytest tests/cli

## Protocol changes

The gRPC API is defined in:

    proto/math.proto

After changing the protobuf definition, regenerate the Python bindings:

    python tools/generate_proto.py

Then run:

    pytest

Generated files are located under:

    src/nmath/generated/