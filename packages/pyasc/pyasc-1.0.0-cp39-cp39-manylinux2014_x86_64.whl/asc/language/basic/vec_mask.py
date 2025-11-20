# Copyright (c) 2025 AISS Group, Harbin Institute of Technology.
# This program is free software, you can redistribute it and/or modify it under the terms and conditions of
# CANN Open Software License Agreement Version 2.0 (the "License").
# Please refer to the License for details. You may not use this file except in compliance with the License.
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
# See LICENSE in the root of the software repository for the full text of the License.
from typing import Optional, overload

from ..._C import ir
from ..core.dtype import KnownTypes as KT
from ..core.dtype import DataType
from ..core.ir_value import RuntimeInt, materialize_ir_value as _mat
from ..core.utils import OverloadDispatcher, require_jit, global_builder
from ..core.enums import MaskMode


@overload
def set_vector_mask(length: int, dtype: DataType, mode: Optional[MaskMode] = MaskMode.NORMAL) -> None: 
    ...


@overload
def set_vector_mask(mask_high: int, mask_low: int, dtype: DataType, 
                    mode: Optional[MaskMode] = MaskMode.NORMAL) -> None: 
    ...


@require_jit
def set_vector_mask(*args, dtype: DataType, mode: MaskMode = MaskMode.NORMAL) -> None:
    builder = global_builder.get_ir_builder()
    if not isinstance(builder, ir.Builder):
        raise TypeError("global_builder must provide an ir.Builder")

    dispatcher = OverloadDispatcher("set_vector_mask")

    @dispatcher.register_auto
    def _(length: RuntimeInt, dtype: DataType, mode: MaskMode = MaskMode.NORMAL):
        builder.create_asc_SetVectorMaskL0Op(
            _mat(length, KT.int32).to_ir(),
            dtype.to_ir(),
            ir.MaskMode.symbolize(mode)
        )

    @dispatcher.register_auto
    def _(mask_high: RuntimeInt, mask_low: RuntimeInt, dtype: DataType, mode: MaskMode = MaskMode.NORMAL):
        builder.create_asc_SetVectorMaskL1Op(
            _mat(mask_high, KT.uint64).to_ir(),
            _mat(mask_low, KT.uint64).to_ir(),
            dtype.to_ir(),
            ir.MaskMode.symbolize(mode)
        )

    dispatcher(*args, dtype=dtype, mode=mode)



