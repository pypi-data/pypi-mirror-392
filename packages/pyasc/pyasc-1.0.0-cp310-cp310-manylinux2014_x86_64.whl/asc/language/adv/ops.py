# This program is free software, you can redistribute it and/or modify it.
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# This file is a part of the CANN Open Software.
# Licensed under CANN Open Software License Agreement Version 2.0 (the "License").
# Please refer to the License for details. You may not use this file except in compliance with the License.
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
# See LICENSE in the root of the software repository for the full text of the License.

from typing import Optional, Tuple, Union, overload

from ..core.dtype import KnownTypes
from ..core.ir_value import RuntimeFloat, RuntimeInt, RuntimeNumeric, \
                            materialize_ir_value as _mat, RuntimeBool
from ..core.tensor import LocalTensor
from ..core.utils import check_type, require_jit, global_builder
from ..fwk.tpipe import TPipe
from .matmul import Matmul
from .tiling import TCubeTiling, RmsNormTiling, SoftmaxTiling
from .types import QuantConfig


@overload
def quant(dst: LocalTensor, src: LocalTensor, scale: float, offset: float, count: Optional[int] = None,
          temp_buffer: Optional[LocalTensor] = None, reuse_source: bool = False,
          config: Optional[QuantConfig] = None) -> None:
    ...


@require_jit
def quant(dst: LocalTensor, src: LocalTensor, scale: RuntimeFloat, offset: RuntimeFloat,
          count: Optional[RuntimeInt] = None, temp_buffer: Optional[LocalTensor] = None, reuse_source: bool = False,
          config: Optional[QuantConfig] = None) -> None:
    scale = _mat(scale, src.dtype).to_ir()
    offset = _mat(offset, src.dtype).to_ir()
    count = _mat(count).to_ir() if count is not None else None
    temp_buffer = temp_buffer.to_ir() if temp_buffer is not None else None
    config = config.to_ir() if config is not None else None
    global_builder.get_ir_builder().create_asc_QuantOp(isReuseSource=reuse_source, dstTensor=dst.to_ir(),
                                                       srcTensor=src.to_ir(), scale=scale, offset=offset,
                                                       calCount=count, sharedTmpBuffer=temp_buffer, config=config)


@require_jit
def register_matmul(pipe: TPipe, matmul: Matmul, tiling: Optional[TCubeTiling] = None) -> None:
    ir_tiling = tiling.to_ir() if tiling is not None else None
    global_builder.get_ir_builder().create_asc_RegistMatmulObjOp(pipe.to_ir(), matmul.to_ir(), ir_tiling)


@overload
def rmsnorm(dst: LocalTensor, src: LocalTensor, gamma: LocalTensor, epsilon: Union[float, int], tiling: RmsNormTiling,
            temp_buffer: Optional[LocalTensor] = None, basic_block: bool = False) -> None:
    ...


@require_jit
def rmsnorm(dst: LocalTensor, src: LocalTensor, gamma: LocalTensor, epsilon: RuntimeNumeric, tiling: RmsNormTiling,
            temp_buffer: Optional[LocalTensor] = None, basic_block: bool = False) -> None:
    temp_buffer = temp_buffer.to_ir() if temp_buffer is not None else None
    epsilon = _mat(epsilon, src.dtype)
    global_builder.get_ir_builder().create_asc_RmsNormOp(basicBlock=basic_block, dst=dst.to_ir(), src=src.to_ir(),
                                                         gamma=gamma.to_ir(), epsilon=epsilon.to_ir(),
                                                         tiling=tiling.to_ir(), sharedTmpBuffer=temp_buffer)


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


# Math Library


def math_op_impl(tensors: Tuple[LocalTensor], count: Optional[RuntimeInt], temp_buffer: Optional[LocalTensor], \
                 is_reuse_source: RuntimeBool, build_method: str) -> None:
    if count is not None:
        check_type("count", count, RuntimeInt)
        count = _mat(count, KnownTypes.int32).to_ir()
    if temp_buffer is not None:
        check_type("temp_buffer", temp_buffer, LocalTensor)
        temp_buffer = temp_buffer.to_ir()
    is_reuse_source = _mat(is_reuse_source, KnownTypes.bit).to_ir()
    getattr(global_builder.get_ir_builder(), build_method)(*(t.to_ir() for t in tensors), sharedTmpBuffer=temp_buffer,
                                                           calCount=count, isReuseSource=is_reuse_source)


@overload
def acos(dst: LocalTensor, src: LocalTensor, count: Optional[int] = None,
         temp_buffer: Optional[LocalTensor] = None, is_reuse_source: bool = False) -> None:
    ...


@require_jit
def acos(dst: LocalTensor, src: LocalTensor, count: Optional[RuntimeInt] = None,
         temp_buffer: Optional[LocalTensor] = None, is_reuse_source: RuntimeBool = False) -> None:
    math_op_impl((dst, src), count, temp_buffer, is_reuse_source, "create_asc_AcosOp")


@overload
def acosh(dst: LocalTensor, src: LocalTensor, count: Optional[int] = None,
          temp_buffer: Optional[LocalTensor] = None, is_reuse_source: bool = False) -> None:
    ...


@require_jit
def acosh(dst: LocalTensor, src: LocalTensor, count: Optional[RuntimeInt] = None,
          temp_buffer: Optional[LocalTensor] = None, is_reuse_source: RuntimeBool = False) -> None:
    math_op_impl((dst, src), count, temp_buffer, is_reuse_source, "create_asc_AcoshOp")


@overload
def asin(dst: LocalTensor, src: LocalTensor, count: Optional[int] = None,
         temp_buffer: Optional[LocalTensor] = None, is_reuse_source: bool = False) -> None:
    ...


@require_jit
def asin(dst: LocalTensor, src: LocalTensor, count: Optional[RuntimeInt] = None,
         temp_buffer: Optional[LocalTensor] = None, is_reuse_source: RuntimeBool = False) -> None:
    math_op_impl((dst, src), count, temp_buffer, is_reuse_source, "create_asc_AsinOp")


@overload
def asinh(dst: LocalTensor, src: LocalTensor, count: Optional[int] = None,
          temp_buffer: Optional[LocalTensor] = None, is_reuse_source: bool = False) -> None:
    ...


@require_jit
def asinh(dst: LocalTensor, src: LocalTensor, count: Optional[RuntimeInt] = None,
          temp_buffer: Optional[LocalTensor] = None, is_reuse_source: RuntimeBool = False) -> None:
    math_op_impl((dst, src), count, temp_buffer, is_reuse_source, "create_asc_AsinhOp")


@overload
def atan(dst: LocalTensor, src: LocalTensor, count: Optional[int] = None,
         temp_buffer: Optional[LocalTensor] = None, is_reuse_source: bool = False) -> None:
    ...


@require_jit
def atan(dst: LocalTensor, src: LocalTensor, count: Optional[RuntimeInt] = None,
         temp_buffer: Optional[LocalTensor] = None, is_reuse_source: RuntimeBool = False) -> None:
    math_op_impl((dst, src), count, temp_buffer, is_reuse_source, "create_asc_AtanOp")


@overload
def atanh(dst: LocalTensor, src: LocalTensor, count: Optional[int] = None,
          temp_buffer: Optional[LocalTensor] = None, is_reuse_source: bool = False) -> None:
    ...


@require_jit
def atanh(dst: LocalTensor, src: LocalTensor, count: Optional[RuntimeInt] = None,
          temp_buffer: Optional[LocalTensor] = None, is_reuse_source: RuntimeBool = False) -> None:
    math_op_impl((dst, src), count, temp_buffer, is_reuse_source, "create_asc_AtanhOp")


@overload
def ceil(dst: LocalTensor, src: LocalTensor, count: Optional[int] = None,
         temp_buffer: Optional[LocalTensor] = None, is_reuse_source: bool = False) -> None:
    ...


@require_jit
def ceil(dst: LocalTensor, src: LocalTensor, count: Optional[RuntimeInt] = None,
         temp_buffer: Optional[LocalTensor] = None, is_reuse_source: RuntimeBool = False) -> None:
    math_op_impl((dst, src), count, temp_buffer, is_reuse_source, "create_asc_CeilOp")


@overload
def cos(dst: LocalTensor, src: LocalTensor, count: Optional[int] = None,
        temp_buffer: Optional[LocalTensor] = None, is_reuse_source: bool = False) -> None:
    ...


@require_jit
def cos(dst: LocalTensor, src: LocalTensor, count: Optional[RuntimeInt] = None,
        temp_buffer: Optional[LocalTensor] = None, is_reuse_source: RuntimeBool = False) -> None:
    math_op_impl((dst, src), count, temp_buffer, is_reuse_source, "create_asc_CosOp")


@overload
def cosh(dst: LocalTensor, src: LocalTensor, count: Optional[int] = None,
         temp_buffer: Optional[LocalTensor] = None, is_reuse_source: bool = False) -> None:
    ...


@require_jit
def cosh(dst: LocalTensor, src: LocalTensor, count: Optional[RuntimeInt] = None,
         temp_buffer: Optional[LocalTensor] = None, is_reuse_source: RuntimeBool = False) -> None:
    math_op_impl((dst, src), count, temp_buffer, is_reuse_source, "create_asc_CoshOp")


@overload
def digamma(dst: LocalTensor, src: LocalTensor, count: Optional[int] = None,
            temp_buffer: Optional[LocalTensor] = None, is_reuse_source: bool = False) -> None:
    ...


@require_jit
def digamma(dst: LocalTensor, src: LocalTensor, count: Optional[RuntimeInt] = None,
            temp_buffer: Optional[LocalTensor] = None, is_reuse_source: RuntimeBool = False) -> None:
    math_op_impl((dst, src), count, temp_buffer, is_reuse_source, "create_asc_DigammaOp")


@overload
def erf(dst: LocalTensor, src: LocalTensor, count: Optional[int] = None,
        temp_buffer: Optional[LocalTensor] = None, is_reuse_source: bool = False) -> None:
    ...


@require_jit
def erf(dst: LocalTensor, src: LocalTensor, count: Optional[RuntimeInt] = None,
        temp_buffer: Optional[LocalTensor] = None, is_reuse_source: RuntimeBool = False) -> None:
    math_op_impl((dst, src), count, temp_buffer, is_reuse_source, "create_asc_ErfOp")


@overload
def erfc(dst: LocalTensor, src: LocalTensor, count: Optional[int] = None,
         temp_buffer: Optional[LocalTensor] = None, is_reuse_source: bool = False) -> None:
    ...


@require_jit
def erfc(dst: LocalTensor, src: LocalTensor, count: Optional[RuntimeInt] = None,
         temp_buffer: Optional[LocalTensor] = None, is_reuse_source: RuntimeBool = False) -> None:
    math_op_impl((dst, src), count, temp_buffer, is_reuse_source, "create_asc_ErfcOp")


@overload
def exp(dst: LocalTensor, src: LocalTensor, count: int, taylor_expand_level: int, 
        temp_buffer: Optional[LocalTensor] = None, is_reuse_source: bool = False) -> None:
    ...


@require_jit
def exp(dst: LocalTensor, src: LocalTensor, count: RuntimeInt, taylor_expand_level: RuntimeInt, \
        temp_buffer: Optional[LocalTensor] = None, is_reuse_source: RuntimeBool = False) -> None:
    count = _mat(count, KnownTypes.uint32).to_ir()
    is_reuse_source = _mat(is_reuse_source, KnownTypes.bit).to_ir()
    taylor_expand_level = _mat(taylor_expand_level, KnownTypes.uint8).to_ir()
    if temp_buffer is not None:
        check_type("temp_buffer", temp_buffer, LocalTensor)
        temp_buffer = temp_buffer.to_ir()
    builder = global_builder.get_ir_builder()
    builder.create_asc_ExpOp(dst.to_ir(), src.to_ir(), count, taylor_expand_level, temp_buffer, is_reuse_source)


@overload
def floor(dst: LocalTensor, src: LocalTensor, count: Optional[int] = None,
          temp_buffer: Optional[LocalTensor] = None, is_reuse_source: bool = False) -> None:
    ...


@require_jit
def floor(dst: LocalTensor, src: LocalTensor, count: Optional[RuntimeInt] = None,
          temp_buffer: Optional[LocalTensor] = None, is_reuse_source: RuntimeBool = False) -> None:
    math_op_impl((dst, src), count, temp_buffer, is_reuse_source, "create_asc_FloorOp")


@overload
def frac(dst: LocalTensor, src: LocalTensor, count: Optional[int] = None,
         temp_buffer: Optional[LocalTensor] = None, is_reuse_source: bool = False) -> None:
    ...


@require_jit
def frac(dst: LocalTensor, src: LocalTensor, count: Optional[RuntimeInt] = None,
         temp_buffer: Optional[LocalTensor] = None, is_reuse_source: RuntimeBool = False) -> None:
    math_op_impl((dst, src), count, temp_buffer, is_reuse_source, "create_asc_FracOp")


@overload
def lgamma(dst: LocalTensor, src: LocalTensor, count: Optional[int] = None,
           temp_buffer: Optional[LocalTensor] = None, is_reuse_source: bool = False) -> None:
    ...


@require_jit
def lgamma(dst: LocalTensor, src: LocalTensor, count: Optional[RuntimeInt] = None,
           temp_buffer: Optional[LocalTensor] = None, is_reuse_source: RuntimeBool = False) -> None:
    math_op_impl((dst, src), count, temp_buffer, is_reuse_source, "create_asc_LgammaOp")


@overload
def log(dst: LocalTensor, src: LocalTensor, count: Optional[int] = None,
        temp_buffer: Optional[LocalTensor] = None, is_reuse_source: bool = False) -> None:
    ...


@require_jit
def log(dst: LocalTensor, src: LocalTensor, count: Optional[RuntimeInt] = None,
        temp_buffer: Optional[LocalTensor] = None, is_reuse_source: RuntimeBool = False) -> None:
    math_op_impl((dst, src), count, temp_buffer, is_reuse_source, "create_asc_LogOp")


@overload
def round(dst: LocalTensor, src: LocalTensor, count: Optional[int] = None,
          temp_buffer: Optional[LocalTensor] = None, is_reuse_source: bool = False) -> None:
    ...


@require_jit
def round(dst: LocalTensor, src: LocalTensor, count: Optional[RuntimeInt] = None,
          temp_buffer: Optional[LocalTensor] = None, is_reuse_source: RuntimeBool = False) -> None:
    math_op_impl((dst, src), count, temp_buffer, is_reuse_source, "create_asc_RoundOp")


@overload
def sign(dst: LocalTensor, src: LocalTensor, count: Optional[int] = None,
         temp_buffer: Optional[LocalTensor] = None, is_reuse_source: bool = False) -> None:
    ...


@require_jit
def sign(dst: LocalTensor, src: LocalTensor, count: Optional[RuntimeInt] = None,
         temp_buffer: Optional[LocalTensor] = None, is_reuse_source: RuntimeBool = False) -> None:
    math_op_impl((dst, src), count, temp_buffer, is_reuse_source, "create_asc_SignOp")


@overload
def sin(dst: LocalTensor, src: LocalTensor, count: Optional[int] = None,
        temp_buffer: Optional[LocalTensor] = None, is_reuse_source: bool = False) -> None:
    ...


@require_jit
def sin(dst: LocalTensor, src: LocalTensor, count: Optional[RuntimeInt] = None,
        temp_buffer: Optional[LocalTensor] = None, is_reuse_source: RuntimeBool = False) -> None:
    math_op_impl((dst, src), count, temp_buffer, is_reuse_source, "create_asc_SinOp")


@overload
def sinh(dst: LocalTensor, src: LocalTensor, count: Optional[int] = None,
         temp_buffer: Optional[LocalTensor] = None, is_reuse_source: bool = False) -> None:
    ...


@require_jit
def sinh(dst: LocalTensor, src: LocalTensor, count: Optional[RuntimeInt] = None,
         temp_buffer: Optional[LocalTensor] = None, is_reuse_source: RuntimeBool = False) -> None:
    math_op_impl((dst, src), count, temp_buffer, is_reuse_source, "create_asc_SinhOp")


@overload
def tan(dst: LocalTensor, src: LocalTensor, count: Optional[int] = None,
        temp_buffer: Optional[LocalTensor] = None, is_reuse_source: bool = False) -> None:
    ...


@require_jit
def tan(dst: LocalTensor, src: LocalTensor, count: Optional[RuntimeInt] = None,
        temp_buffer: Optional[LocalTensor] = None, is_reuse_source: RuntimeBool = False) -> None:
    math_op_impl((dst, src), count, temp_buffer, is_reuse_source, "create_asc_TanOp")


@overload
def tanh(dst: LocalTensor, src: LocalTensor, count: Optional[int] = None,
         temp_buffer: Optional[LocalTensor] = None, is_reuse_source: bool = False) -> None:
    ...


@require_jit
def tanh(dst: LocalTensor, src: LocalTensor, count: Optional[RuntimeInt] = None,
         temp_buffer: Optional[LocalTensor] = None, is_reuse_source: RuntimeBool = False) -> None:
    math_op_impl((dst, src), count, temp_buffer, is_reuse_source, "create_asc_TanhOp")


@overload
def trunc(dst: LocalTensor, src: LocalTensor, count: Optional[int] = None,
          temp_buffer: Optional[LocalTensor] = None, is_reuse_source: bool = False) -> None:
    ...


@require_jit
def trunc(dst: LocalTensor, src: LocalTensor, count: Optional[RuntimeInt] = None,
          temp_buffer: Optional[LocalTensor] = None, is_reuse_source: RuntimeBool = False) -> None:
    math_op_impl((dst, src), count, temp_buffer, is_reuse_source, "create_asc_TruncOp")


@overload
def power(dst: LocalTensor, src0: LocalTensor, src1: LocalTensor, count: Optional[int] = None,
          temp_buffer: Optional[LocalTensor] = None, is_reuse_source: bool = False) -> None:
    ...


@require_jit
def power(dst: LocalTensor, src0: LocalTensor, src1: LocalTensor, count: Optional[RuntimeInt] = None,
          temp_buffer: Optional[LocalTensor] = None, is_reuse_source: RuntimeBool = False) -> None:
    math_op_impl((dst, src0, src1), count, temp_buffer, is_reuse_source, "create_asc_PowerOp")


@overload
def xor(dst: LocalTensor, src0: LocalTensor, src1: LocalTensor, count: Optional[int] = None,
        temp_buffer: Optional[LocalTensor] = None, is_reuse_source: bool = False) -> None:
    ...


@require_jit
def xor(dst: LocalTensor, src0: LocalTensor, src1: LocalTensor, count: Optional[RuntimeInt] = None,
        temp_buffer: Optional[LocalTensor] = None, is_reuse_source: RuntimeBool = False) -> None:
    math_op_impl((dst, src0, src1), count, temp_buffer, is_reuse_source, "create_asc_XorOp")


@overload
def axpy(dst: LocalTensor, src: LocalTensor, scalar: Union[float, int], count: Optional[int] = None,
         temp_buffer: Optional[LocalTensor] = None, is_reuse_source: bool = False) -> None:
    ...


@require_jit
def axpy(dst: LocalTensor, src: LocalTensor, scalar: RuntimeNumeric, count: Optional[RuntimeInt] = None,
         temp_buffer: Optional[LocalTensor] = None, is_reuse_source: RuntimeBool = False) -> None:
    scalar = _mat(scalar, src.dtype)
    math_op_impl((dst, src, scalar), count, temp_buffer, is_reuse_source, "create_asc_AxpyOp")
