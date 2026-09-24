from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Operator(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OPERATOR_UNSPECIFIED: _ClassVar[Operator]
    OPERATOR_ADD: _ClassVar[Operator]
    OPERATOR_SUB: _ClassVar[Operator]
    OPERATOR_MUL: _ClassVar[Operator]
    OPERATOR_DIV: _ClassVar[Operator]

class OperationStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STATUS_SUCCESS: _ClassVar[OperationStatus]
    STATUS_DIV_BY_ZERO: _ClassVar[OperationStatus]
    STATUS_NAN: _ClassVar[OperationStatus]
    STATUS_ERROR: _ClassVar[OperationStatus]
OPERATOR_UNSPECIFIED: Operator
OPERATOR_ADD: Operator
OPERATOR_SUB: Operator
OPERATOR_MUL: Operator
OPERATOR_DIV: Operator
STATUS_SUCCESS: OperationStatus
STATUS_DIV_BY_ZERO: OperationStatus
STATUS_NAN: OperationStatus
STATUS_ERROR: OperationStatus

class PingRequest(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class PingResponse(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class BinaryOperationRequest(_message.Message):
    __slots__ = ("left_operand", "right_operand", "operator")
    LEFT_OPERAND_FIELD_NUMBER: _ClassVar[int]
    RIGHT_OPERAND_FIELD_NUMBER: _ClassVar[int]
    OPERATOR_FIELD_NUMBER: _ClassVar[int]
    left_operand: float
    right_operand: float
    operator: Operator
    def __init__(self, left_operand: _Optional[float] = ..., right_operand: _Optional[float] = ..., operator: _Optional[_Union[Operator, str]] = ...) -> None: ...

class BinaryOperationResponse(_message.Message):
    __slots__ = ("result", "status")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    result: float
    status: OperationStatus
    def __init__(self, result: _Optional[float] = ..., status: _Optional[_Union[OperationStatus, str]] = ...) -> None: ...
