# gRPC-Connected NumPy Math Engine

A small, test-driven mathematical execution system that accepts a restricted LaTeX-like mathematical language at the CLI, compiles it into a typed intermediate representation (IR), translates that representation into gRPC requests, and executes the operations remotely using NumPy.

The project starts deliberately small:

```text
CLI
  ↓
Unix Domain Socket
  ↓
Bridge (Parser & Execution Planner)
  ↓
gRPC
  ↓
NumPy server
  ↓
Result

```

The long-term goal is to evolve this from a simple remote calculator into a small **distributed numerical execution engine** with a math-language frontend.

---

## 1. Vision

The central idea is to separate **mathematical notation**, **mathematical meaning**, **wire representation**, and **numerical execution**.

```text
LaTeX        = input / presentation language
AST / IR     = mathematical meaning
protobuf     = network representation
NumPy        = execution backend
gRPC         = transport / remote execution

```

The server should **not** understand LaTeX.

Instead, the client bridge parses and compiles mathematical expressions into a stable, typed representation. The server receives that representation and executes it.

This separation is important because it lets the project evolve independently:

* the frontend can become more expressive without changing the numerical runtime;


* the runtime can change from NumPy to another backend without changing the parser;


* a future Python, JSON, or other frontend can reuse the same IR;


* unit tests can isolate parsing, compilation, networking, and numerical execution.



---

# 2. High-Level Architecture

```text
                         Local process
┌───────────────────────────────────────────────────────────────┐
│                                                               │
│  CLI                                                          │
│  nmath "2 + 3"                                                │
│       │                                                       │
│       ▼  (Unix Domain Socket)                                 │
│                                                               │
│  Bridge Process                                               │
│       │                                                       │
│       ▼                                                       │
│  Lexer / AST Parser (M2)                                      │
│       │                                                       │
│       ▼                                                       │
│  Typed Math IR / Execution Planner                            │
│       │                                                       │
│       ▼                                                       │
│  gRPC client                                                  │
│                                                               │
└───────────────────────────┬───────────────────────────────────┘
                            │
                          gRPC
                            │
                            ▼
┌───────────────────────────────────────────────────────────────┐
│                        NumPy Server                           │
│                                                               │
│  gRPC service                                                 │
│       │                                                       │
│       ▼                                                       │
│  Operation dispatcher                                         │
│       │                                                       │
│       ▼                                                       │
│  NumPy runtime                                                │
│       │                                                       │
│       ▼                                                       │
│  Result / structured error                                    │
│                                                               │
└───────────────────────────────────────────────────────────────┘

```

A key design rule is:

> **Do not make the NumPy server parse LaTeX.**
> 

The server should receive a typed mathematical representation.

---

# 3. Core Design Principle: Treat This as a Compiler

The project is easier to reason about as a tiny compiler pipeline than as a "LaTeX-to-gRPC parser".

```text
                Frontend
                  │
            LaTeX input
                  │
                  ▼
             Lexer / Parser
                  │
                  ▼
              Math AST
                  │
                  ▼
             Typed IR
                  │
                  ▼
          Execution planner
                  │
                  ▼
              protobuf
                  │
                  ▼
                gRPC
                  │
                  ▼
              NumPy runtime

```

This creates three major software layers.

## Frontend

Responsible for:

```text
LaTeX → AST

```

Examples:

```latex
2 + 3
\frac{2+3}{4}
\sin(2) + 3^2

```

The frontend should initially support only a deliberately small subset of LaTeX.

## Compiler

Responsible for:

```text
AST → typed IR → execution plan

```

This is where the system can eventually perform:

* syntax validation;


* type validation;


* shape validation;


* constant folding;


* common-subexpression elimination;


* operation fusion;


* execution planning;


* graph optimization.



## Runtime

Responsible for:

```text
execution plan → NumPy computation

```

The runtime can be accessed:

* locally for unit tests and debugging;


* remotely through gRPC for integration and distributed execution.



---

# 4. Start With a Very Small Language

Do **not** attempt to support arbitrary LaTeX.

LaTeX is a huge typesetting language and supporting all mathematical syntax would create unnecessary complexity.

Instead, define a small mathematical DSL represented using LaTeX-like notation.

The first language could support:

```text
NUMBER
+
-
*
/
()

```

Examples:

```latex
2 + 3
10 - 4
6 * 7
8 / 2
(2 + 3) * 4

```

Later, add mathematical notation such as:

```latex
\frac{a}{b}
a^b
\sqrt{a}
\sin(a)
\cos(a)
\log(a)

```

Eventually, vector and matrix notation can be introduced.

---

# 5. The Mathematical Intermediate Representation

The IR is the most important abstraction in the system.

A useful conceptual model is:

```text
Expression
├── Scalar
├── Complex
├── Tensor
├── UnaryOp
└── BinaryOp

```

For a simple expression:

```latex
2 + 3

```

the IR could be:

```text
BinaryOp(
    operation = ADD,
    left = Scalar(2),
    right = Scalar(3)
)

```

For:

```latex
(2 + 3) * 4

```

the tree becomes:

```text
Multiply
├── Add
│   ├── Scalar(2)
│   └── Scalar(3)
└── Scalar(4)

```

The parser creates the IR.
The gRPC bridge serializes the IR.
The server executes the IR.

This means the IR should not contain parser-specific details such as raw LaTeX strings.

---

# 6. Proposed Value Model

A future generic numerical value should support different mathematical types.

```text
Value
├── Scalar
├── Complex
└── Tensor

```

with metadata such as:

```text
dtype
shape

```

For example:

```text
Value
    type: tensor
    dtype: float64
    shape: [1024, 1024]

```

A protobuf representation could conceptually look like:

```protobuf
message Value {
    oneof kind {
        double scalar = 1;
        Complex complex = 2;
        Tensor tensor = 3;
    }
}

```

This makes it possible for the same operation to work across different value types.

For example:

```text
ADD

```

could represent:

```text
scalar + scalar
vector + vector
matrix + matrix

```

provided the type and shape rules allow it.

Prefer a generic operation model over separate APIs such as:

```text
AddScalar()
AddVector()
AddMatrix()

```

A single semantic `ADD(Value, Value)` is easier to extend.

---

# 7. Proposed gRPC API

For the first milestones, keep the service simple.

Conceptually:

```protobuf
enum Operator {
    OPERATOR_UNSPECIFIED = 0;
    OPERATOR_ADD = 1;
    OPERATOR_SUB = 2;
    OPERATOR_MUL = 3;
    OPERATOR_DIV = 4;
}

enum OperationStatus {
    STATUS_SUCCESS = 0;
    STATUS_DIV_BY_ZERO = 1;
    STATUS_NAN = 2;
    STATUS_ERROR = 3;
}

message BinaryOperationRequest {
    double left_operand = 1;
    double right_operand = 2;
    Operator operator = 3;
}

message BinaryOperationResponse {
    double result = 1;
    OperationStatus status = 2;
}

service MathService {
    rpc Ping(PingRequest) returns (PingResponse);
    rpc BinaryOperation(BinaryOperationRequest) returns (BinaryOperationResponse);
}

```

The protocol should evolve together with the IR.

---

# 8. Milestone Plan

## M0 — gRPC Connectivity

### Goal

Establish a working CLI → gRPC server connection.

### Example

```bash
nmath ping

```

### Expected behavior

```text
server: OK

```

### Tests

* CLI starts;


* client can connect;


* gRPC service responds;


* server can be started independently;


* connection failure produces a useful error.



---

## M1 — Basic Scalar Math With Unix Socket Bridge

### Goal

Support basic binary scalar arithmetic over a local Unix domain socket bridge.

Supported operations:

```text
+
-
*
/

```

### Data flow

```text
CLI (nmath "2 + 3")
  ↓
Unix Socket (/tmp/nmath.sock)
  ↓
Bridge Regex Parser
  ↓
BinaryOperationRequest(ADD, 2, 3)
  ↓
gRPC
  ↓
5

```

### Parser behavior

```text
"2 + 3"
→ Add(2.0, 3.0)

```

```text
"8 / 2"
→ Div(8.0, 2.0)

```

### Invalid syntax

Malformed syntax acts as a diagnostic fallback by invoking the `Ping` RPC to verify server availability.

---

## M2 — Recursive Scalar Expressions & AST Compilation

### Goal

Once two-operand expressions work, introduce nested expressions. The M1 Regex parser must be replaced with a formal Lexer/Parser AST pipeline (e.g., Python `ast` or `lark`).

Examples:

```latex
(2 + 3) * 4
\frac{2+3}{5}
(10 - 2) / (3 + 1)

```

The parser must now create recursive expression trees.

For:

```latex
\frac{3^2 + \sqrt{16}}{2}

```

the structure could conceptually be:

```text
Divide
├── Add
│   ├── Pow(3, 2)
│   └── Sqrt(16)
└── 2

```

The exact AST representation can differ, but the semantic structure should be explicit.

---

# 9. M3 — Rich Scalar Mathematics

Add more unary and binary operations.

## Binary operations

```text
+
-
*
/
^

```

## Unary operations

```text
sqrt
sin
cos
tan
exp
log

```

Example:

```latex
\frac{\sin(2) + 3^2}{4}

```

The language is now becoming a small mathematical expression language.

This milestone should focus on:

* recursive parsing;


* operator precedence;


* associativity;


* unary expressions;


* numeric semantics;


* predictable errors.



---

# 10. Complex Numbers

Complex numbers can be added as a separate type-system milestone.

Example:

```latex
(2 + 3i)(4 - i)

```

The value model then becomes:

```text
Scalar
Complex
Tensor

```

The parser and compiler should distinguish:

```text
2

```

from:

```text
2 + 3i

```

This should be treated as a type-system extension rather than mixed into the parser without a clear model.

---

# 11. M4 — Vector Math

This is the point where NumPy becomes especially useful.

Example:

```latex
[1,2,3] + [4,5,6]

```

Result:

```text
[5,7,9]

```

The runtime now needs values with:

```text
dtype
shape
data

```

For example:

```text
Tensor<float64>
shape = [3]

```

### Important vector tests

Valid:

```text
[1,2,3] + [4,5,6]

```

Invalid:

```text
[1,2,3] + [4,5]

```

Also test:

* empty vectors;


* scalar/vector operations;


* dtype conversion;


* NaN;


* infinity;


* shape compatibility;


* unsupported operations.



---

# 12. Broadcasting

NumPy supports broadcasting, but the project should decide whether to inherit all NumPy broadcasting rules immediately.

For the first vector milestone, it may be better to make shape compatibility explicit and conservative.

For example:

```text
[1,2,3] + [4,5,6]

```

is clearly valid.

But:

```text
[1,2,3] + [4,5]

```

should produce a structured shape error unless broadcasting semantics have explicitly been implemented.

Later, broadcasting can become a deliberate compiler/runtime feature.

---

# 13. M5 — Matrices and General Tensors

Once vectors are supported, extend the same `Tensor` abstraction to matrices and higher-dimensional arrays.

Example matrix notation:

```latex
\begin{bmatrix}
1 & 2 \\
3 & 4
\end{bmatrix}

```

The IR does not need separate vector and matrix operation classes if both are tensors.

Conceptually:

```text
Tensor
    dtype = float64
    shape = [2, 2]

```

This naturally leads to:

```text
vector
matrix
3D tensor
N-D tensor

```

being instances of the same fundamental numerical value model.

---

# 14. M6 — Complete Execution Graphs

The initial prototype may execute an expression as multiple RPC calls.

For:

```latex
(2 + 3) * 4

```

a naïve implementation could do:

```text
RPC 1: ADD(2, 3)
RPC 2: MUL(result, 4)

```

This is easy to implement and useful as a first step.

However, many RPC round trips will become inefficient for large expressions.

The longer-term architecture should send a complete computation graph in one request.

For example:

```text
node 0 = CONST(2)
node 1 = CONST(3)
node 2 = ADD(0,1)
node 3 = CONST(4)
node 4 = MUL(2,3)

root = 4

```

The server can then execute the complete graph.

Conceptually:

```protobuf
message Expression {
    repeated Node nodes = 1;
    uint32 root = 2;
}

```

This design is much closer to a numerical execution engine.

---

# 15. Execution Graph Benefits

Once expressions are represented as graphs, future optimizations become possible.

Examples:

```text
constant folding
common-subexpression elimination
operation fusion
caching
parallel execution
batching

```

For example:

```latex
(2+3)^2 + (2+3)^3

```

could initially calculate `2+3` twice.

A later compiler could transform it into:

```text
t0 = 2 + 3
t1 = t0^2
t2 = t0^3
t3 = t1 + t2

```

The same IR therefore becomes a foundation for optimization.

---

# 16. Error Model

The public API should use structured mathematical errors rather than leaking Python exceptions.

A useful error taxonomy is:

```text
INVALID_SYNTAX
UNSUPPORTED_OPERATION
TYPE_MISMATCH
SHAPE_MISMATCH
DIVISION_BY_ZERO
INVALID_VALUE
SERVER_ERROR

```

Errors should be stable enough that clients can handle them programmatically.

---

# 17. Suggested Repository Layout

```text
nmath/
├── pyproject.toml
├── README.md
├── .env
│
├── proto/
│   └── math.proto
│
├── src/
│   └── nmath/
│       ├── config.py
│       │
│       ├── cli/
│       │   └── main.py
│       │
│       ├── bridge/
│       │   └── main.py
│       │
│       ├── parser/ (M2)
│       │   ├── lexer.py
│       │   └── parser.py
│       │
│       ├── ir/ (M2)
│       │   ├── nodes.py
│       │   └── types.py
│       │
│       ├── compiler/ (M2)
│       │   └── planner.py
│       │
│       ├── client/
│       │   └── service.py
│       │
│       └── server/
│           ├── main.py
│           ├── service.py
│           └── numpy_runtime.py
│
└── tests/
    ├── unit/
    ├── e2e/
    ├── contract/
    └── integration/

```

The exact package names are flexible; the important part is keeping the boundaries visible.

---

# 18. TDD Development Loop

Each feature should follow the same process:

```text
1. Define mathematical behavior
2. Write failing parser tests
3. Write failing IR tests
4. Write failing bridge tests
5. Write failing runtime tests
6. Implement the smallest change
7. Add an end-to-end integration test
8. Refactor

```

The TDD emphasis should be on **behavioral contracts**, not implementation details.

---

# 19. Suggested Initial Test Matrix

## Scalar arithmetic

| Input | Expected |
| --- | --- |
| `2 + 3` | `5` |
| `5 - 2` | `3` |
| `4 * 7` | `28` |
| `8 / 2` | `4` |

## Invalid input

| Input | Expected |
| --- | --- |
| `2 +` | syntax error

 |
| `foo` | syntax error

 |
| `1 / 0` | defined numerical error

 |

The final expected representation should be defined precisely in tests rather than assumed from Python's string formatting.

---

# 20. Proposed Milestone Roadmap

```text
M0  Connectivity
    └── CLI → gRPC → Ping

M1  Basic scalar binary operations
    └── CLI → Socket Bridge → Regex Parser → gRPC → NumPy

M2  Recursive scalar expressions
    └── Replace Regex with AST compiler pipeline (parentheses, precedence)

M3  Rich scalar mathematics
    └── powers, sqrt, sin, cos, exp, log

M4  Complex numbers
    └── scalar + complex + complex operations

M5  Vectors / tensors
    └── NumPy arrays, dtype, shape

M6  Matrices
    └── matrix-specific and tensor operations

M7  Complete execution graphs
    └── one gRPC request per expression

M8  Graph optimization
    └── folding, CSE, fusion, batching, caching

```

Milestones can overlap, but each should have a clear acceptance boundary.
