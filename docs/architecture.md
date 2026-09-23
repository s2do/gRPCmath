# Architecture

## Overview

`nmath` is a Python-based mathematical execution engine with a gRPC
client/server architecture.

Milestone M0 establishes the basic communication path between a command-line
client and a gRPC server.

The current M0 implementation provides a single RPC:

```text
MathService.Ping(PingRequest) -> PingResponse
````

The `Ping` operation is used to verify that the client can reach the server
and that the gRPC service is correctly configured.

---

## System Architecture

The current M0 architecture consists of four main layers:

```text
┌───────────────────────────────────────────────┐
│                   User                        │
└───────────────────────┬───────────────────────┘
                        │
                        │ command
                        ▼
┌───────────────────────────────────────────────┐
│                nmath CLI                      │
│             src/nmath/cli/                    │
└───────────────────────┬───────────────────────┘
                        │
                        │ Python API
                        ▼
┌───────────────────────────────────────────────┐
│              MathClient                       │
│           src/nmath/client/                   │
└───────────────────────┬───────────────────────┘
                        │
                        │ gRPC
                        │ Ping RPC
                        ▼
┌───────────────────────────────────────────────┐
│              gRPC Server                      │
│           src/nmath/server/                   │
│                                               │
│              MathService                      │
└───────────────────────┬───────────────────────┘
                        │
                        │ PingResponse
                        ▼
                    Client
```

The client and server communicate through the Protocol Buffer contract
defined in `proto/math.proto`.

---

## Repository Structure

The relevant M0 components are organized as follows:

```text
gRPCmath/
├── proto/
│   └── math.proto
│
├── src/
│   └── nmath/
│       ├── cli/
│       │   └── main.py
│       │
│       ├── client/
│       │   └── service.py
│       │
│       ├── generated/
│       │   ├── math_pb2.py
│       │   ├── math_pb2.pyi
│       │   └── math_pb2_grpc.py
│       │
│       └── server/
│           ├── main.py
│           └── service.py
│
├── tests/
│   ├── cli/
│   ├── contract/
│   ├── integration/
│   ├── unit/
│   └── test_smoke.py
│
└── tools/
    └── generate_proto.py
```

---

## Components

### Protocol Definition

The public gRPC API is defined in:

```text
proto/math.proto
```

This file is the source of truth for the RPC interface.

The M0 service is:

```proto
service MathService {
    rpc Ping(PingRequest) returns (PingResponse);
}
```

The corresponding messages are:

```proto
message PingRequest {
    string message = 1;
}

message PingResponse {
    string message = 1;
}
```

The Protocol Buffer definition should be changed before changing the generated
Python bindings.

---

### Generated gRPC Code

The files under:

```text
src/nmath/generated/
```

are generated from `proto/math.proto`.

They provide the Python representations of the Protocol Buffer messages and
the gRPC client/server interfaces.

Generated files should not be edited manually.

They can be regenerated with:

```bash
python tools/generate_proto.py
```

---

### Server

The server is implemented in:

```text
src/nmath/server/
```

#### `server/service.py`

`MathService` implements the gRPC service defined by the Protocol Buffer
contract.

For M0, the service implements `Ping`.

The implementation receives a `PingRequest` and returns a `PingResponse`.

For example:

```text
Request:
    message = "hello"

Response:
    message = "pong: hello"
```

#### `server/main.py`

`server/main.py` is responsible for creating and running the gRPC server.

The default server address is:

```text
127.0.0.1:50051
```

The server can also bind to a dynamically allocated port during tests.

---

### Client

The client implementation is located in:

```text
src/nmath/client/service.py
```

`MathClient` provides a small Python abstraction over the generated gRPC
stub.

The client:

1. Creates a gRPC channel.
2. Creates a `MathServiceStub`.
3. Constructs Protocol Buffer requests.
4. Calls the corresponding RPC.
5. Returns the relevant response data.

For M0, the client exposes:

```python
client.ping(message)
```

---

### CLI

The command-line interface is implemented in:

```text
src/nmath/cli/main.py
```

The CLI currently exposes the `ping` command.

Example:

```bash
nmath ping
```

which uses the default server:

```text
127.0.0.1:50051
```

A custom server and message can be specified:

```bash
nmath ping \
    --server 127.0.0.1:50052 \
    --message "hello"
```

The CLI delegates the actual RPC communication to `MathClient`.

This keeps command-line argument handling separate from the gRPC client
implementation.

---

## Request Flow

For the command:

```bash
nmath ping --message "hello"
```

the request flows through the system as follows:

```text
User
 │
 │ nmath ping --message "hello"
 ▼
CLI
 │
 │ MathClient.ping("hello")
 ▼
MathClient
 │
 │ Ping(PingRequest(message="hello"))
 ▼
gRPC channel
 │
 ▼
MathService.Ping()
 │
 │ PingResponse(message="pong: hello")
 ▼
gRPC channel
 │
 ▼
MathClient
 │
 │ "pong: hello"
 ▼
CLI
 │
 ▼
stdout
```

This flow verifies the complete M0 communication path.

---

## Service Boundary

The Protocol Buffer definition creates a clear boundary between the client
and server.

```text
             Client Process
┌───────────────────────────────┐
│                               │
│  CLI                          │
│   │                           │
│   ▼                           │
│  MathClient                   │
│                               │
└───────────────┬───────────────┘
                │
                │ gRPC
                │
════════════════╪════════════════
                │
                │ MathService API
                │
════════════════╪════════════════
                │
┌───────────────▼───────────────┐
│        Server Process         │
│                               │
│  MathService                  │
│                               │
└───────────────────────────────┘
```

The client does not directly access server implementation classes.

The server does not depend on CLI code.

Communication between the two sides occurs through the gRPC API.

---

## Design Responsibilities

| Component            | Responsibility                                       |
| -------------------- | ---------------------------------------------------- |
| `proto/math.proto`   | Defines the gRPC API contract                        |
| `generated/`         | Contains generated Protocol Buffer and gRPC bindings |
| `server/service.py`  | Implements `MathService`                             |
| `server/main.py`     | Creates and runs the gRPC server                     |
| `client/service.py`  | Provides the Python client abstraction               |
| `cli/main.py`        | Handles command-line interaction                     |
| `tests/contract/`    | Verifies the Protocol Buffer contract                |
| `tests/unit/`        | Tests individual components                          |
| `tests/integration/` | Tests client/server communication                    |
| `tests/cli/`         | Tests CLI argument handling                          |

---

## Testing Architecture

The test suite is divided according to the architectural boundaries.

### Contract Tests

Located in:

```text
tests/contract/
```

These tests verify that the generated Protocol Buffer and gRPC definitions
provide the expected messages and service interfaces.

---

### Unit Tests

Located in:

```text
tests/unit/
```

Unit tests verify individual components without requiring a running gRPC
server.

For example:

```text
MathService.Ping()
MathClient.ping()
MathClient.close()
```

---

### Integration Tests

Located in:

```text
tests/integration/
```

Integration tests verify communication between the client and the gRPC
server.

The tests create a server, connect a client to it, perform an RPC, and verify
the response.

---

### CLI Tests

Located in:

```text
tests/cli/
```

These tests verify command-line argument parsing and CLI behavior without
requiring an externally running server.

---

## M0 Scope

M0 establishes connectivity and the basic project architecture.

The following capabilities are implemented:

* Python package structure
* Protocol Buffer API definition
* gRPC server
* gRPC client
* `nmath` CLI
* `Ping` RPC
* Unit tests
* Contract tests
* Integration tests
* CLI tests

The primary verification is:

```bash
nmath-server
```

followed by:

```bash
nmath ping
```

which should produce:

```text
pong: hello
```

---

## Out of Scope for M0

M0 does not implement the mathematical execution engine.

The following functionality is therefore outside the scope of this
milestone:

* mathematical operations
* NumPy-backed execution
* expression parsing
* execution jobs
* result persistence
* authentication
* authorization
* production deployment
* distributed execution
* performance optimization

These capabilities can be introduced in later milestones without changing
the basic client/server separation established by M0.

---

## Architectural Direction

M0 intentionally keeps the architecture small.

The main architectural boundary is:

```text
CLI / Client
      │
      │ gRPC API
      ▼
    Server
```

Future mathematical functionality should be added behind the service
boundary rather than coupling the CLI directly to the mathematical execution
implementation.

The Protocol Buffer API remains the contract between clients and the
server.

