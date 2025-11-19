# This program is free software, you can redistribute it and/or modify it.
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# This file is a part of the CANN Open Software.
# Licensed under CANN Open Software License Agreement Version 2.0 (the "License").
# Please refer to the License for details. You may not use this file except in compliance with the License.
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
# See LICENSE in the root of the software repository for the full text of the License.

from typing import Union, overload

from ..core.dtype import KnownTypes
from ..core.ir_value import RuntimeInt, RuntimeNumeric, materialize_ir_value as _mat
from ..core.tensor import LocalTensor
from ..core.utils import require_jit, global_builder


@overload
def duplicate(dst: LocalTensor, scalar: Union[int, float], count: int) -> None:
    ...


@require_jit
def duplicate(dst: LocalTensor, scalar: RuntimeNumeric, count: RuntimeInt) -> None:
    global_builder.get_ir_builder().create_asc_DuplicateL2Op(dst.to_ir(),
                                                             _mat(scalar, dst.dtype).to_ir(),
                                                             _mat(count, KnownTypes.int_).to_ir())
