# This program is free software, you can redistribute it and/or modify it.
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# This file is a part of the CANN Open Software.
# Licensed under CANN Open Software License Agreement Version 2.0 (the "License").
# Please refer to the License for details. You may not use this file except in compliance with the License.
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
# See LICENSE in the root of the software repository for the full text of the License.

from .ops import (
    quant,
    register_matmul,
    rmsnorm,
    softmax,
    # Math library
    acos,
    acosh,
    asin,
    asinh,
    atan,
    atanh,
    ceil,
    cos,
    cosh,
    digamma,
    erf,
    erfc,
    exp,
    floor,
    frac,
    lgamma,
    log,
    round,
    sign,
    sin,
    sinh,
    tan,
    tanh,
    trunc,
    power,
    xor,
    axpy,
)
from .matmul import (
    Matmul,
    MatmulType,
    get_matmul_api_tiling,
)
from .tiling import (
    MatmulApiStaticTiling,
    RmsNormTiling,
    SoftmaxTiling,
    TCubeTiling,
)
from .types import (
    MatmulConfig,
    QuantConfig,
)

__all__ = [
    # .ops
    "quant",
    "register_matmul",
    "rmsnorm",
    "softmax",
    "acos",
    "acosh",
    "asin",
    "asinh",
    "atan",
    "atanh",
    "ceil",
    "cos",
    "cosh",
    "digamma",
    "erf",
    "erfc",
    "exp",
    "floor",
    "frac",
    "lgamma",
    "log",
    "round",
    "sign",
    "sin",
    "sinh",
    "tan",
    "tanh",
    "trunc",
    "power",
    "xor",
    "axpy",
    # .matmul
    "Matmul",
    "MatmulType",
    "get_matmul_api_tiling",
    # .tiling
    "MatmulApiStaticTiling",
    "RmsNormTiling",
    "SoftmaxTiling",
    "TCubeTiling",
    # .types
    "MatmulConfig",
    "QuantConfig",
]
