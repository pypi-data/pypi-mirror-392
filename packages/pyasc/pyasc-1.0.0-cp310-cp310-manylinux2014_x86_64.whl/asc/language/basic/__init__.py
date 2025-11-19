# This program is free software, you can redistribute it and/or modify it.
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# This file is a part of the CANN Open Software.
# Licensed under CANN Open Software License Agreement Version 2.0 (the "License").
# Please refer to the License for details. You may not use this file except in compliance with the License.
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
# See LICENSE in the root of the software repository for the full text of the License.

from .common import (
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

from .data_copy import data_copy
from .dump_tensor import dump_tensor, printf
from .sys_var import (
    get_block_idx,
    get_block_num,
)
from .vec_binary import (
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
from .vec_binary_scalar import (
    adds,
    leaky_relu,
    maxs,
    mins,
    muls,
    shift_left,
    shift_right,
)
from .vec_duplicate import duplicate
from .vec_vconv import (
    add_relu_cast,
    sub_relu_cast,
    set_deq_scale,
    cast_deq,
)
from .vec_unary import (
    abs,
    exp,
    ln,
    bitwise_not,
    reciprocal,
    relu,
    rsqrt,
    sqrt,
)

__all__ = [
    # .common
    "ffts_cross_core_sync",
    "get_sys_workspace",
    "is_cube_core",
    "is_vector_core",
    "pipe_barrier",
    "pop_stack_buffer",
    "set_ffts_base_addr",
    "set_sys_workspace_force",
    "set_flag",
    "wait_flag",
    "set_deq_scale",
    "cast_deq",
    # .data_copy
    "data_copy",
    # .dump_tensor
    "dump_tensor",
    "printf",
    # .sys_var
    "get_block_idx",
    "get_block_num",
    # .vec_binary
    "add",
    "add_deq_relu",
    "add_relu",
    "add_relu_cast",
    "bilinear_interpolation",
    "bitwise_and",
    "bitwise_or",
    "div",
    "fused_mul_add",
    "fused_mul_add_relu",
    "max",
    "min",
    "mul",
    "mul_add_dst",
    "mul_cast",
    "sub",
    "sub_relu",
    "sub_relu_cast",
    # .vec_binary_scalar
    "adds",
    "leaky_relu",
    "maxs",
    "mins",
    "muls",
    "shift_left",
    "shift_right",
    # .vec_duplicate
    "duplicate",
    # .vec_unary
    "abs",
    "exp",
    "ln",
    "bitwise_not",
    "reciprocal",
    "relu",
    "rsqrt",
    "sqrt",
]
