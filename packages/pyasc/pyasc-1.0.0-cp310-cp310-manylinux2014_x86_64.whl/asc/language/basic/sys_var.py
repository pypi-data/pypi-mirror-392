# This program is free software, you can redistribute it and/or modify it.
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# This file is a part of the CANN Open Software.
# Licensed under CANN Open Software License Agreement Version 2.0 (the "License").
# Please refer to the License for details. You may not use this file except in compliance with the License.
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
# See LICENSE in the root of the software repository for the full text of the License.

from typing import overload

from ..core.dtype import KnownTypes
from ..core.ir_value import PlainValue, RuntimeInt
from ..core.utils import require_jit, global_builder


@overload
def get_block_idx() -> int:
    ...


@require_jit
def get_block_idx() -> RuntimeInt:
    return PlainValue(global_builder.get_ir_builder().create_asc_GetBlockIdxOp(KnownTypes.int_.to_ir()))


@overload
def get_block_num() -> int:
    ...


@require_jit
def get_block_num() -> RuntimeInt:
    return PlainValue(global_builder.get_ir_builder().create_asc_GetBlockNumOp(KnownTypes.int_.to_ir()))
