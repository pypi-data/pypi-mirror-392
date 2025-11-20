# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# This program is free software, you can redistribute it and/or modify it under the terms and conditions of
# CANN Open Software License Agreement Version 2.0 (the "License").
# Please refer to the License for details. You may not use this file except in compliance with the License.
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
# See LICENSE in the root of the software repository for the full text of the License.

from typing import Optional

from ..core.tensor import LocalTensor
from ..core.utils import require_jit, global_builder
from .tiling import SoftmaxTiling


@require_jit
def softmax(dst: LocalTensor, sum: LocalTensor, max: LocalTensor, src: LocalTensor, tiling: SoftmaxTiling,
            temp_buffer: Optional[LocalTensor] = None, reuse_source: bool = False, basic_block: bool = False,
            data_format_nz: bool = False) -> None:
    temp_buffer = temp_buffer.to_ir() if temp_buffer is not None else None
    global_builder.get_ir_builder().create_asc_SoftMaxOp(reuseSource=reuse_source, basicBlock=basic_block,
                                                         dataFormatNZ=data_format_nz, dst=dst.to_ir(),
                                                         sumTensor=sum.to_ir(), maxTensor=max.to_ir(), src=src.to_ir(),
                                                         sharedTmpBuffer=temp_buffer, tiling=tiling.to_ir(),
                                                         softmaxShapeInfo=None)
