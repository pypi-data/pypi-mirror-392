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
from ..core.ir_value import RuntimeInt, materialize_ir_value as _mat
from ..core.tensor import BaseTensor, GlobalTensor, LocalTensor
from ..core.types import DataCopyEnhancedParams, DataCopyParams
from ..core.utils import OverloadDispatcher, require_jit, global_builder


@overload
def data_copy(dst: LocalTensor, src: GlobalTensor, count: int) -> None:
    ...


@overload
def data_copy(dst: LocalTensor, src: LocalTensor, count: int) -> None:
    ...


@overload
def data_copy(dst: GlobalTensor, src: LocalTensor, count: int) -> None:
    ...


@overload
def data_copy(dst: LocalTensor, src: GlobalTensor, params: DataCopyParams) -> None:
    ...


@overload
def data_copy(dst: LocalTensor, src: LocalTensor, params: DataCopyParams) -> None:
    ...


@overload
def data_copy(dst: GlobalTensor, src: LocalTensor, params: DataCopyParams) -> None:
    ...


@overload
def data_copy(dst: LocalTensor, src: GlobalTensor, params: DataCopyParams,
              enhanced_params: DataCopyEnhancedParams) -> None:
    ...


@overload
def data_copy(dst: LocalTensor, src: LocalTensor, params: DataCopyParams,
              enhanced_params: DataCopyEnhancedParams) -> None:
    ...


@overload
def data_copy(dst: GlobalTensor, src: LocalTensor, params: DataCopyParams,
              enhanced_params: DataCopyEnhancedParams) -> None:
    ...


@overload
def data_copy(dst: GlobalTensor, src: LocalTensor, slice_list1: list, slice_list2: list, dim_value: int) -> None:
    ...


@overload
def data_copy(dst: LocalTensor, src: GlobalTensor, slice_list1: list, slice_list2: list, dim_value: int) -> None:
    ...


@require_jit
def data_copy(dst: BaseTensor, src: BaseTensor, *args, **kwargs) -> None:
    dispatcher = OverloadDispatcher(__name__)
    builder = global_builder.get_ir_builder()

    @dispatcher.register_auto
    def _(params: DataCopyParams):
        builder.create_asc_DataCopyL0Op(dst.to_ir(), src.to_ir(), params.to_ir())

    @dispatcher.register_auto
    def _(count: RuntimeInt):
        builder.create_asc_DataCopyL2Op(dst.to_ir(), src.to_ir(), _mat(count, KnownTypes.int_).to_ir())

    @dispatcher.register_auto
    def _(params: DataCopyParams, enhanced_params: DataCopyEnhancedParams):
        builder.create_asc_DataCopyEnhancedOp(dst.to_ir(), src.to_ir(), params.to_ir(), enhanced_params.to_ir())

    @dispatcher.register_auto
    def _(slice_list1: list, slice_list2: list, dim_value: RuntimeInt):
        slice_list1 = [value.to_ir() for value in slice_list1]
        slice_list2 = [value.to_ir() for value in slice_list2]
        builder.create_asc_DataCopySliceOp(dst.to_ir(), src.to_ir(), slice_list1, slice_list2,
                                           _mat(dim_value, KnownTypes.uint32).to_ir())

    dispatcher(*args, **kwargs)
