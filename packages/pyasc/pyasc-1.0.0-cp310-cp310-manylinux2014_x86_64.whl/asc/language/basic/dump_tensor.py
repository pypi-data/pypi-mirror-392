# This program is free software, you can redistribute it and/or modify it.
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# This file is a part of the CANN Open Software.
# Licensed under CANN Open Software License Agreement Version 2.0 (the "License").
# Please refer to the License for details. You may not use this file except in compliance with the License.
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
# See LICENSE in the root of the software repository for the full text of the License.

from typing import Callable, Optional, TypeVar, overload

from ..core.dtype import KnownTypes
from ..core.ir_value import IRValue, RuntimeInt, materialize_ir_value as _mat
from ..core.tensor import BaseTensor, GlobalTensor, LocalTensor
from ..core.types import ShapeInfo
from ..core.utils import require_jit, global_builder, check_type

T = TypeVar("T", bound=Callable)


def set_docstring(op: Optional[str] = None, cpp_name: Optional[str] = None) -> Callable[[T], T]:
    cpp_signature = ""
    if cpp_name == "printf":
        cpp_signature = """
    The corresponding Ascend C functions have the following signatures:

    .. code-block:: c++

        namespace AscendC {

        __aicore__ inline void printf(__gm__ const char* fmt, Args&&... args)
        __aicore__ inline void PRINTF(__gm__ const char* fmt, Args&&... args)

        } // namespace AscendC


        """
        docstr = f"""
        Enable print debug information when running NPU mode.
        {cpp_signature}

        Parameters:
            fmt(char*): the format control string
            args(Args): input arguments to print
        """
    else:
        cpp_signature = """
    The corresponding Ascend C functions have the following signatures:

    .. code-block:: c++

        namespace AscendC {

        template <typename T>
        __aicore__ inline void DumpTensor(const LocalTensor<T>& tensor, uint32_t desc, uint32_t dumpSize)
        template <typename T>
        __aicore__ inline void DumpTensor(const GlobalTensor<T>& tensor, uint32_t desc, uint32_t dumpSize)
        template <typename T>
        __aicore__ inline void DumpTensor(const LocalTensor<T>& tensor, uint32_t desc,
            uint32_t dumpSize, const ShapeInfo& shapeInfo)
        template <typename T>
        __aicore__ inline void DumpTensor(const GlobalTensor<T>& tensor, uint32_t desc,
            uint32_t dumpSize, const ShapeInfo& shapeInfo)

        } // namespace AscendC


        """
        docstr = f"""
        Enable dump tensor data when running NPU mode.
        {cpp_signature}

        Parameters:
            tensor(GlobalTenor/LocalTensor): the tensor need to dump
            desc(uint32_t): custom addtional info(line number or other digits)
            dumpSize(uint32_t): the number of elements need to dump
            shapeInfo(ShapeInfo): the shape info of tensor
        """

    def decorator(fn: T) -> T:
        fn.__doc__ = docstr
        return fn

    return decorator


@overload
def dump_tensor(tensor: GlobalTensor, desc: int, dump_size: int, shape_info: Optional[ShapeInfo] = None) -> None:
    ...


@overload
def dump_tensor(tensor: LocalTensor, desc: int, dump_size: int, shape_info: Optional[ShapeInfo] = None) -> None:
    ...


@require_jit
@set_docstring("``dump_tensor``", cpp_name="DumpTensor")
def dump_tensor(tensor: BaseTensor, desc: RuntimeInt, dump_size: RuntimeInt,
                shape_info: Optional[ShapeInfo] = None) -> None:
    check_type("desc", desc, RuntimeInt)
    check_type("dump_size", dump_size, RuntimeInt)
    if shape_info is not None:
        check_type("shape_info", shape_info, ShapeInfo)
        shape_info = shape_info.to_ir()
    global_builder.get_ir_builder().create_asc_DumpTensorOp(tensor.to_ir(),
                                                            _mat(desc, KnownTypes.uint32).to_ir(),
                                                            _mat(dump_size, KnownTypes.uint32).to_ir(),
                                                            shapeInfo=shape_info)


@require_jit
@set_docstring("``printf``", cpp_name="printf")
def printf(desc: str, *params) -> None:
    var_ir_values = []
    desc_str_list = desc.split("%s")
    new_desc = ""
    str_index = 0
    for var in params:
        if isinstance(var, str):
            new_desc += desc_str_list[str_index] + var
            str_index += 1
        elif isinstance(var, IRValue):
            var_ir_values.append(var.to_ir())
        else:
            var_ir_values.append(_mat(var).to_ir())
    if new_desc != "":
        new_desc += desc_str_list[str_index]
        global_builder.get_ir_builder().create_asc_PrintfOp(new_desc, var_ir_values)
    else:
        global_builder.get_ir_builder().create_asc_PrintfOp(desc, var_ir_values)
