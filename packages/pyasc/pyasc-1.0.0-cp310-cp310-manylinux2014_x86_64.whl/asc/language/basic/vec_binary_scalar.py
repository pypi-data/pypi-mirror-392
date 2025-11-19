# This program is free software, you can redistribute it and/or modify it.
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# This file is a part of the CANN Open Software.
# Licensed under CANN Open Software License Agreement Version 2.0 (the "License").
# Please refer to the License for details. You may not use this file except in compliance with the License.
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
# See LICENSE in the root of the software repository for the full text of the License.

from typing import Any, Callable, Dict, List, Tuple, Union, overload

from ..._C import ir
from ..core.dtype import KnownTypes as KT
from ..core.ir_value import RuntimeInt, RuntimeNumeric, materialize_ir_value as _mat
from ..core.tensor import LocalTensor
from ..core.utils import OverloadDispatcher, require_jit, global_builder
from ..core.types import UnaryRepeatParams


def op_impl(callee: str, dst: LocalTensor, src: LocalTensor, scalar: RuntimeNumeric, args: Tuple[Any],
            kwargs: Dict[str, Any], build_l0: Callable, build_l1: Callable, build_l2: Callable) -> None:
    builder = build_l0.__self__
    if not isinstance(builder, ir.Builder):
        raise TypeError("Input builder must be ir.Builder")
    scalar = _mat(scalar, src.dtype).to_ir()
    dispatcher = OverloadDispatcher(callee)

    @dispatcher.register_auto
    def _(mask: RuntimeInt, repeat_times: RuntimeInt, params: UnaryRepeatParams):
        build_l0(dst.to_ir(), src.to_ir(), scalar,
                 _mat(mask, KT.uint64).to_ir(),
                 _mat(repeat_times, KT.int8).to_ir(), params.to_ir())

    @dispatcher.register_auto
    def _(mask: list, repeat_times: RuntimeInt, params: UnaryRepeatParams):
        mask = [_mat(v, KT.uint64).to_ir() for v in mask]
        build_l1(dst.to_ir(), src.to_ir(), scalar, mask, _mat(repeat_times, KT.int8).to_ir(), params.to_ir())

    @dispatcher.register_auto
    def _(count: RuntimeInt):
        build_l2(dst.to_ir(), src.to_ir(), scalar, _mat(count, KT.int32).to_ir())

    dispatcher(*args, **kwargs)


@overload
def adds(dst: LocalTensor, src: LocalTensor, scalar: Union[int, float], count: int) -> None:
    ...


@overload
def adds(dst: LocalTensor, src: LocalTensor, scalar: Union[int, float], mask: int, repeat_times: int,
         params: UnaryRepeatParams) -> None:
    ...


@overload
def adds(dst: LocalTensor, src: LocalTensor, scalar: Union[int, float], mask: List[int], repeat_times: int,
         params: UnaryRepeatParams) -> None:
    ...


@require_jit
def adds(dst: LocalTensor, src: LocalTensor, scalar: RuntimeNumeric, *args, **kwargs) -> None:
    builder = global_builder.get_ir_builder()
    op_impl("adds", dst, src, scalar, args, kwargs, builder.create_asc_AddsL0Op, builder.create_asc_AddsL1Op,
            builder.create_asc_AddsL2Op)


@overload
def leaky_relu(dst: LocalTensor, src: LocalTensor, scalar: Union[int, float], count: int) -> None:
    ...


@overload
def leaky_relu(dst: LocalTensor, src: LocalTensor, scalar: Union[int, float], mask: int, repeat_times: int,
               params: UnaryRepeatParams) -> None:
    ...


@overload
def leaky_relu(dst: LocalTensor, src: LocalTensor, scalar: Union[int, float], mask: List[int], repeat_times: int,
               params: UnaryRepeatParams) -> None:
    ...


@require_jit
def leaky_relu(dst: LocalTensor, src: LocalTensor, scalar: RuntimeNumeric, *args, **kwargs) -> None:
    builder = global_builder.get_ir_builder()
    op_impl("leaky_relu", dst, src, scalar, args, kwargs, builder.create_asc_LeakyReluL0Op,
            builder.create_asc_LeakyReluL1Op, builder.create_asc_LeakyReluL2Op)


@overload
def maxs(dst: LocalTensor, src: LocalTensor, scalar: Union[int, float], count: int) -> None:
    ...


@overload
def maxs(dst: LocalTensor, src: LocalTensor, scalar: Union[int, float], mask: int, repeat_times: int,
         params: UnaryRepeatParams) -> None:
    ...


@overload
def maxs(dst: LocalTensor, src: LocalTensor, scalar: Union[int, float], mask: List[int], repeat_times: int,
         params: UnaryRepeatParams) -> None:
    ...


@require_jit
def maxs(dst: LocalTensor, src: LocalTensor, scalar: RuntimeNumeric, *args, **kwargs) -> None:
    builder = global_builder.get_ir_builder()
    op_impl("maxs", dst, src, scalar, args, kwargs, builder.create_asc_MaxsL0Op, builder.create_asc_MaxsL1Op,
            builder.create_asc_MaxsL2Op)


@overload
def mins(dst: LocalTensor, src: LocalTensor, scalar: Union[int, float], count: int) -> None:
    ...


@overload
def mins(dst: LocalTensor, src: LocalTensor, scalar: Union[int, float], mask: int, repeat_times: int,
         params: UnaryRepeatParams) -> None:
    ...


@overload
def mins(dst: LocalTensor, src: LocalTensor, scalar: Union[int, float], mask: List[int], repeat_times: int,
         params: UnaryRepeatParams) -> None:
    ...


@require_jit
def mins(dst: LocalTensor, src: LocalTensor, scalar: RuntimeNumeric, *args, **kwargs) -> None:
    builder = global_builder.get_ir_builder()
    op_impl("mins", dst, src, scalar, args, kwargs, builder.create_asc_MinsL0Op, builder.create_asc_MinsL1Op,
            builder.create_asc_MinsL2Op)


@overload
def muls(dst: LocalTensor, src: LocalTensor, scalar: Union[int, float], count: int) -> None:
    ...


@overload
def muls(dst: LocalTensor, src: LocalTensor, scalar: Union[int, float], mask: int, repeat_times: int,
         params: UnaryRepeatParams) -> None:
    ...


@overload
def muls(dst: LocalTensor, src: LocalTensor, scalar: Union[int, float], mask: List[int], repeat_times: int,
         params: UnaryRepeatParams) -> None:
    ...


@require_jit
def muls(dst: LocalTensor, src: LocalTensor, scalar: RuntimeNumeric, *args, **kwargs) -> None:
    builder = global_builder.get_ir_builder()
    op_impl("muls", dst, src, scalar, args, kwargs, builder.create_asc_MulsL0Op, builder.create_asc_MulsL1Op,
            builder.create_asc_MulsL2Op)


@overload
def shift_left(dst: LocalTensor, src: LocalTensor, scalar: Union[int, float], count: int) -> None:
    ...


@overload
def shift_left(dst: LocalTensor, src: LocalTensor, scalar: Union[int, float], mask: int, repeat_times: int,
               params: UnaryRepeatParams) -> None:
    ...


@overload
def shift_left(dst: LocalTensor, src: LocalTensor, scalar: Union[int, float], mask: List[int], repeat_times: int,
               params: UnaryRepeatParams) -> None:
    ...


@require_jit
def shift_left(dst: LocalTensor, src: LocalTensor, scalar: RuntimeNumeric, *args, **kwargs) -> None:
    builder = global_builder.get_ir_builder()
    op_impl("shift_left", dst, src, scalar, args, kwargs, builder.create_asc_ShiftLeftL0Op,
            builder.create_asc_ShiftLeftL1Op, builder.create_asc_ShiftLeftL2Op)


@overload
def shift_right(dst: LocalTensor, src: LocalTensor, scalar: Union[int, float], count: int) -> None:
    ...


@overload
def shift_right(dst: LocalTensor, src: LocalTensor, scalar: Union[int, float], mask: int, repeat_times: int,
                params: UnaryRepeatParams) -> None:
    ...


@overload
def shift_right(dst: LocalTensor, src: LocalTensor, scalar: Union[int, float], mask: List[int], repeat_times: int,
                params: UnaryRepeatParams) -> None:
    ...


@require_jit
def shift_right(dst: LocalTensor, src: LocalTensor, scalar: RuntimeNumeric, *args, **kwargs) -> None:
    builder = global_builder.get_ir_builder()
    op_impl("shift_right", dst, src, scalar, args, kwargs, builder.create_asc_ShiftRightL0Op,
            builder.create_asc_ShiftRightL1Op, builder.create_asc_ShiftRightL2Op)
