# This program is free software, you can redistribute it and/or modify it.
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# This file is a part of the CANN Open Software.
# Licensed under CANN Open Software License Agreement Version 2.0 (the "License").
# Please refer to the License for details. You may not use this file except in compliance with the License.
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
# See LICENSE in the root of the software repository for the full text of the License.

from . import adv
from . import basic
from . import core
from . import fwk

from .basic import __all__ as basic_all
from .core import __all__ as core_all
from .fwk import __all__ as fwk_all

# basic
from .basic.common import (
    ffts_cross_core_sync,
    get_sys_workspace,
    is_cube_core,
    is_vector_core,
    pipe_barrier,
    pop_stack_buffer,
    set_ffts_base_addr,
    set_sys_workspace_force,
    set_flag,
    wait_flag,
)

from .basic.data_copy import data_copy
from .basic.dump_tensor import dump_tensor, printf
from .basic.sys_var import (
    get_block_idx,
    get_block_num,
)
from .basic.vec_binary import (
    add,
    add_deq_relu,
    add_relu,
    bilinear_interpolation,
    bitwise_and,
    bitwise_or,
    div,
    fused_mul_add,
    fused_mul_add_relu,
    max,
    min,
    mul,
    mul_add_dst,
    mul_cast,
    sub,
    sub_relu,
)
from .basic.vec_binary_scalar import (
    adds,
    leaky_relu,
    maxs,
    mins,
    muls,
    shift_left,
    shift_right,
)
from .basic.vec_duplicate import duplicate
from .basic.vec_vconv import (
    add_relu_cast,
    sub_relu_cast,
    set_deq_scale,
    cast_deq,
)
from .basic.vec_unary import (
    abs,
    exp,
    ln,
    bitwise_not,
    reciprocal,
    relu,
    rsqrt,
    sqrt,
)

# core
from .core.array import array
from .core.constexpr import ConstExpr
from .core.dtype import (
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
from .core.enums import (
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
from .core.ir_value import GlobalAddress
from .core.ops import inline, number
from .core.properties import (
    property,
    DEFAULT_C0_SIZE,
    ONE_BLK_SIZE,
    TOTAL_L0C_SIZE,
    TOTAL_L1_SIZE,
)
from .core.range import range, static_range
from .core.tensor import GlobalTensor, LocalTensor
from .core.types import (
    BinaryRepeatParams,
    DataCopyParams,
    DataCopyEnhancedParams,
    ShapeInfo,
    SliceInfo,
    UnaryRepeatParams,
)
from .core.utils import static_assert, ceildiv

# fwk
from .fwk.tpipe import TBuf, TBufPool, TBufHandle, TPipe, TQue, get_tpipe_ptr

__all__ = [
    # .language
    "adv",
    "basic",
    "core",
    "fwk",
]

__all__.extend(basic_all)
__all__.extend(core_all)
__all__.extend(fwk_all)
