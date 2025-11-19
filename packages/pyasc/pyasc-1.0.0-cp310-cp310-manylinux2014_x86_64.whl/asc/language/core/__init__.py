# This program is free software, you can redistribute it and/or modify it.
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# This file is a part of the CANN Open Software.
# Licensed under CANN Open Software License Agreement Version 2.0 (the "License").
# Please refer to the License for details. You may not use this file except in compliance with the License.
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
# See LICENSE in the root of the software repository for the full text of the License.

from .array import array
from .constexpr import ConstExpr
from .dtype import (
    DataType,
    void,
    int8,
    int16,
    int32,
    int64,
    float16,
    float32,
    float64,
    uint8,
    uint16,
    uint32,
    uint64,
    int_,
    half,
    float_,
    double,
)
from .enums import (
    BlockMode,
    CacheMode,
    CacheRwMode,
    CubeFormat,
    DataFormat,
    DeqScale,
    HardEvent,
    PipeID,
    Position,
    pad_t,
    BatchMode,
    IterateMode,
    IterateOrder,
    ScheduleType,
    LayoutMode,
)
from .ir_value import GlobalAddress
from .ops import inline, number
from .properties import (
    property,
    DEFAULT_C0_SIZE,
    ONE_BLK_SIZE,
    TOTAL_L0C_SIZE,
    TOTAL_L1_SIZE,
)
from .range import range, static_range
from .tensor import GlobalTensor, LocalTensor
from .types import (
    BinaryRepeatParams,
    DataCopyParams,
    DataCopyEnhancedParams,
    ShapeInfo,
    SliceInfo,
    UnaryRepeatParams,
)
from .utils import static_assert, ceildiv

__all__ = [
    # .array
    "array",
    # .constexpr
    "ConstExpr",
    # .dtype
    "DataType",
    "void",
    "int8",
    "int16",
    "int32",
    "int64",
    "float16",
    "float32",
    "float64",
    "uint8",
    "uint16",
    "uint32",
    "uint64",
    "int_",
    "half",
    "float_",
    "double",
    # .enums
    "BlockMode",
    "CacheMode",
    "CacheRwMode",
    "CubeFormat",
    "DataFormat",
    "DeqScale",
    "HardEvent",
    "PipeID",
    "Position",
    "pad_t",
    "BatchMode",
    "IterateMode",
    "IterateOrder",
    "ScheduleType",
    "LayoutMode",
    # .ir_value
    "GlobalAddress",
    # .ops
    "inline",
    "number",
    # .property
    "property",
    "DEFAULT_C0_SIZE",
    "ONE_BLK_SIZE",
    "TOTAL_L0C_SIZE",
    "TOTAL_L1_SIZE",
    # .core.range
    "range",
    "static_range",
    # .core.tensor
    "GlobalTensor",
    "LocalTensor",
    # .core.types
    "BinaryRepeatParams",
    "DataCopyEnhancedParams",
    "DataCopyParams",
    "ShapeInfo",
    "SliceInfo",
    "UnaryRepeatParams",
    # .core.utils
    "static_assert",
    "ceildiv",
    # .core.array
    "array",
]
