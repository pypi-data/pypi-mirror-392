# This program is free software, you can redistribute it and/or modify it.
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# This file is a part of the CANN Open Software.
# Licensed under CANN Open Software License Agreement Version 2.0 (the "License").
# Please refer to the License for details. You may not use this file except in compliance with the License.
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
# See LICENSE in the root of the software repository for the full text of the License.

from typing import Any, Callable, Dict, Optional, Tuple, TypeVar

from ..._C import ir
from ..core.dtype import KnownTypes as KT
from ..core.ir_value import RuntimeInt, materialize_ir_value as _mat
from ..core.tensor import LocalTensor
from ..core.utils import DefaultValued, OverloadDispatcher
from ..core.types import BinaryRepeatParams

T = TypeVar("T", bound=Callable)


def check_type(callee: str, dst: LocalTensor, src0: LocalTensor, src1: LocalTensor) -> None:
    valids = {"src": [KT.float16, KT.float32, KT.int16, KT.int32], "dst": [KT.float16, KT.float32, KT.int16, KT.int32]}
    valids_relu = {"src": [KT.float16, KT.float32, KT.int16], "dst": [KT.float16, KT.float32, KT.int16]}
    valids_relu_cast = {"src": [KT.float16, KT.float32, KT.int16], "dst": [KT.int8, KT.float16]}
    valids_int = {"src": [KT.int16, KT.uint16], "dst": [KT.int16, KT.uint16]}
    valids_float = {"src": [KT.float16, KT.float32], "dst": [KT.float16, KT.float32]}

    valids_map = {
        "add": valids,
        "add_deq_relu": {"src": [KT.int32], "dst": [KT.float16]},
        "add_relu": valids_relu,
        "add_relu_cast": valids_relu_cast,
        "bilinear_interpolation": {"src": [KT.float16], "dst": [KT.float16]},
        "bitwise_and": valids_int,
        "bitwise_or": valids_int,
        "div": valids_float,
        "fused_mul_add": valids_float,
        "fused_mul_add_relu": valids_float,
        "max": valids,
        "min": valids,
        "mul": valids,
        "mul_add_dst": valids_float,
        "mul_cast": {"src": [KT.float16], "dst": [KT.int8, KT.uint8]},
        "sub": valids,
        "sub_relu": valids_relu,
        "sub_relu_cast": valids_relu_cast,
    }

    check_dst_src = {"add_deq_relu", "add_relu_cast", "bilinear_interpolation", "mul_cast", "sub_relu_cast"}

    if dst.dtype not in valids_map.get(callee).get("dst"):
        raise TypeError(f"Invalid dst data type, got {dst.dtype}, expect {valids_map.get(callee)}")
    if src0.dtype not in valids_map.get(callee).get("src"):
        raise TypeError(f"Invalid src0 data type, got {dst.dtype}, expect {valids_map.get(callee)}")
    if src1.dtype not in valids_map.get(callee).get("src"):
        raise TypeError(f"Invalid src1 data type, got {dst.dtype}, expect {valids_map.get(callee)}")
    if src0.dtype != src1.dtype:
        raise TypeError("Src0 and src1 must be same type.")
    if callee not in check_dst_src:
        if not (dst.dtype == src0.dtype and dst.dtype == src1.dtype):
            raise TypeError("Src0, src1 and dst must be same type.")


def op_impl(callee: str, dst: LocalTensor, src0: LocalTensor, src1: LocalTensor, args: Tuple[Any],
            kwargs: Dict[str, Any], build_l0: Callable, build_l1: Callable, build_l2: Callable) -> None:
    builder = build_l0.__self__
    if not isinstance(builder, ir.Builder):
        raise TypeError("Input builder must be ir.Builder")
    dispatcher = OverloadDispatcher(callee)

    check_type(callee, dst, src0, src1)

    @dispatcher.register(mask=RuntimeInt, repeat_times=RuntimeInt, params=BinaryRepeatParams, 
                        is_set_mask=DefaultValued(bool, True))
    def _(mask: RuntimeInt, repeat_times: RuntimeInt, params: BinaryRepeatParams, is_set_mask: bool = True):
        build_l0(dst.to_ir(), src0.to_ir(), src1.to_ir(),
                 _mat(mask, KT.uint64).to_ir(), _mat(repeat_times, KT.int8).to_ir(), 
                params.to_ir(), is_set_mask)

    @dispatcher.register(mask=list, repeat_times=RuntimeInt, params=BinaryRepeatParams, 
                        is_set_mask=DefaultValued(bool, True))
    def _(mask: list, repeat_times: RuntimeInt, params: BinaryRepeatParams, is_set_mask: bool = True):
        mask = [_mat(v, KT.uint64).to_ir() for v in mask]
        build_l1(dst.to_ir(), src0.to_ir(), src1.to_ir(), mask, _mat(repeat_times, KT.int8).to_ir(), 
                params.to_ir(), is_set_mask)

    @dispatcher.register_auto
    def _(count: RuntimeInt):
        build_l2(dst.to_ir(), src0.to_ir(), src1.to_ir(), _mat(count, KT.int32).to_ir())

    dispatcher(*args, **kwargs)


def set_binary_docstring(cpp_name: Optional[str] = None, append_text: str = "") -> Callable[[T], T]:
    func_introduction = f"""
        {append_text}
    """

    cpp_signature = f"""
    **对应的Ascend C函数原型**

        .. code-block:: c++

            template <typename T>
            __aicore__ inline void {cpp_name}(const LocalTensor<T>& dst, const LocalTensor<T>& src0,
                                                const LocalTensor<T>& src1, const int32_t& count);

            template <typename T, bool isSetMask = true>
            __aicore__ inline void {cpp_name}(const LocalTensor<T>& dst, const LocalTensor<T>& src0,
                                                const LocalTensor<T>& src1, uint64_t mask[], const uint8_t repeatTimes,
                                                const BinaryRepeatParams& repeatParams);

            template <typename T, bool isSetMask = true>
            __aicore__ inline void {cpp_name}(const LocalTensor<T>& dst, const LocalTensor<T>& src0,
                                                const LocalTensor<T>& src1, uint64_t mask, const uint8_t repeatTimes,
                                                const BinaryRepeatParams& repeatParams);

        """

    param_list = """
    **参数说明**
        - dst: 目的操作数。类型为LocalTensor，支持的TPosition为VECIN/VECCALC/VECOUT。
        - src0, src1: 源操作数。类型为LocalTensor，支持的TPosition为VECIN/VECCALC/VECOUT。
        - count: 参与计算的元素个数。
        - mask: 用于控制每次迭代内参与计算的元素。
        - repeat_times: 重复迭代次数。
        - params: 控制操作数地址步长的参数。
    """
    set_mask_param = ""
    if cpp_name != 'mul_cast':
        set_mask_param = """
        - is_set_mask: 是否在接口内部设置mask。
        """

    docstr = f"""
    {func_introduction}
    {cpp_signature}
    {param_list}
    {set_mask_param}
    """


    def decorator(fn: T) -> T:
        fn.__doc__ = docstr
        return fn

    return decorator
