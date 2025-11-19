# This program is free software, you can redistribute it and/or modify it.
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# This file is a part of the CANN Open Software.
# Licensed under CANN Open Software License Agreement Version 2.0 (the "License").
# Please refer to the License for details. You may not use this file except in compliance with the License.
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
# See LICENSE in the root of the software repository for the full text of the License.

from __future__ import annotations
import itertools
from typing import Any, NoReturn, Optional, Tuple, Union, overload

from ..._C import ir
from ...common.compat import isinstance
from .constexpr import ConstExpr
from .dtype import DataType, KnownTypes
from .enums import CacheMode, CacheRwMode, Position
from .ir_value import GlobalAddress, IRHandle, IRValue, PlainValue, \
                            RuntimeInt, RuntimeNumeric, materialize_ir_value as _mat
from .types import ShapeInfo, TensorShape
from .utils import OverloadDispatcher, require_jit, global_builder, set_tensor_docstring


class BaseTensor(IRValue):

    def __init__(self, dtype: DataType):
        self.dtype = dtype

    @staticmethod
    def ensure_shape(shape: Optional[Any], allow_none: bool = True) -> Optional[TensorShape]:
        if shape is None:
            if allow_none:
                return None
            raise ValueError("Tensor shape must be provided, got None")
        return TensorShape(shape)

    @classmethod
    def from_ir(cls, handle: IRHandle) -> NoReturn:
        raise NotImplementedError(f"{cls.__name__} cannot be constructed from IR handle")


class GlobalTensor(BaseTensor):

    @overload
    def __init__(self, handle: IRHandle) -> None:
        """This contructor should not be called by user"""
        ...

    def __init__(self, handle: Optional[IRHandle] = None) -> None:
        self.shape = None
        if handle is not None:
            dtype = DataType.from_ir(ir.get_element_type(handle.get_type()))
            super().__init__(dtype)
            self.handle = handle
            return

    @require_jit
    def __getitem__(self, slices: Any) -> GlobalTensor:
        builder = global_builder.get_ir_builder()
        if isinstance(slices, RuntimeInt):
            handle = builder.create_asc_GlobalTensorSubIndexOp(self.to_ir().get_type(), self.to_ir(),
                                                               _mat(slices).to_ir())
            return GlobalTensor(handle=handle)
        if isinstance(slices, slice):
            if slices.step is not None or slices.stop is not None:
                raise RuntimeError("Slice operation with provided stop and step is not supported for GlobalTensor")
            handle = builder.create_asc_GlobalTensorSubIndexOp(self.to_ir().get_type(), self.to_ir(),
                                                               _mat(slices.start).to_ir())
            return GlobalTensor(handle=handle)
        raise RuntimeError(f"Tensor subscript operation is not supported with {slices}")

    @classmethod
    def from_ir(cls, handle: IRHandle) -> GlobalTensor:
        return cls(handle=handle)

    def to_ir(self) -> IRHandle:
        return self.handle

    @overload
    def set_global_buffer(self, buffer: Optional[GlobalAddress] = None) -> None:
        ...

    @overload
    def set_global_buffer(self, buffer: Optional[GlobalAddress] = None, buffer_size: Optional[int] = None) -> None:
        ...

    @require_jit
    @set_tensor_docstring(tensor_name="GlobalTensor", api_name="set_global_buffer")
    def set_global_buffer(self, buffer: Optional[GlobalAddress] = None,
                          buffer_size: Optional[RuntimeInt] = None) -> None:

        if buffer is None or buffer.dtype is None:
            raise ValueError("Either DataType or typed GlobalAddress must be provided to instantiate GlobalTensor")
        dtype = buffer.dtype
        super().__init__(dtype)
        builder = global_builder.get_ir_builder()
        ir_type = ir.get_global_tensor_type(dtype.to_ir())
        handle = builder.create_asc_GlobalTensorOp(ir_type)
        self.dtype = dtype
        self.handle = handle

        if buffer_size:
            builder.create_asc_SetGlobalBufferOp(self.to_ir(), buffer.to_ir(), _mat(buffer_size).to_ir())
        else:
            builder.create_asc_SetGlobalBufferOp(self.to_ir(), buffer.to_ir())

    @overload
    def get_phy_addr(self) -> GlobalAddress:
        ...

    @overload
    def get_phy_addr(self, offset: int) -> GlobalAddress:
        ...

    @require_jit
    @set_tensor_docstring(tensor_name="GlobalTensor", api_name="get_phy_addr")
    def get_phy_addr(self, offset: RuntimeInt = 0) -> GlobalAddress:
        builder = global_builder.get_ir_builder()
        ga_type = ir.get_unranked_memref_type(self.dtype.to_ir(), ir.AddressSpace.gm)
        handle = builder.create_asc_GlobalTensorGetPhyAddrOp(ga_type, self.to_ir(),
                                                             _mat(offset, KnownTypes.uint64).to_ir())
        return GlobalAddress(handle)

    @overload
    def set_value(self, offset: int, value: Union[int, float]) -> None:
        ...

    @require_jit
    @set_tensor_docstring(tensor_name="GlobalTensor", api_name="set_value")
    def set_value(self, offset: RuntimeInt, value: RuntimeNumeric) -> None:
        builder = global_builder.get_ir_builder()
        builder.create_asc_GlobalTensorSetValueOp(self.to_ir(),
                                                  _mat(offset, KnownTypes.uint64).to_ir(),
                                                  _mat(value, self.dtype).to_ir())

    @overload
    def get_value(self, offset: int) -> int:
        ...

    @require_jit
    @set_tensor_docstring(tensor_name="GlobalTensor", api_name="get_value")
    def get_value(self, offset: RuntimeInt) -> RuntimeNumeric:
        builder = global_builder.get_ir_builder()
        handle = builder.create_asc_GetValueGlobalTensorOp(self.dtype.to_ir(), self.to_ir(),
                                                           _mat(offset, KnownTypes.uint64).to_ir())
        return PlainValue(handle, self.dtype)

    @overload
    def get_size(self) -> int:
        ...

    @require_jit
    @set_tensor_docstring(tensor_name="GlobalTensor", api_name="get_size")
    def get_size(self) -> RuntimeInt:
        if self.shape is None:
            builder = global_builder.get_ir_builder()
            handle = builder.create_asc_GlobalTensorGetSizeOp(builder.get_ui64_type(), self.to_ir())
            return PlainValue(handle)
        return itertools.accumulate(self.shape, lambda acc, next: acc * next, initial=1)

    @overload
    def set_shape_info(self, shape: Tuple[int, ...]) -> None:
        ...

    @overload
    def set_shape_info(self, shape_info: ShapeInfo) -> None:
        ...

    @require_jit
    @set_tensor_docstring(tensor_name="GlobalTensor", api_name="set_shape_info")
    def set_shape_info(self, shape_info, **args) -> None:
        builder = global_builder.get_ir_builder()
        if isinstance(shape_info, ShapeInfo):
            builder.create_asc_GlobalTensorSetShapeInfoOp(self.to_ir(), shape_info.to_ir())
        else:
            shape_array = [_mat(value, KnownTypes.int_).to_ir() for value in shape_info]
            builder.create_asc_GlobalTensorSetShapeInfoV2Op(self.to_ir(), shape_array)

    @require_jit
    @set_tensor_docstring(tensor_name="GlobalTensor", api_name="get_shape_info")
    def get_shape_info(self) -> ShapeInfo:
        builder = global_builder.get_ir_builder()
        handle = builder.create_asc_GlobalTensorGetShapeInfoOp(builder.get_asc_ShapeInfoType(), self.to_ir())
        return ShapeInfo(handle)

    @require_jit
    @set_tensor_docstring(tensor_name="GlobalTensor", api_name="set_l2_cache_hint")
    def set_l2_cache_hint(self, mode: Optional[CacheMode] = CacheMode.CACHE_MODE_NORMAL, \
                        rw_mode: Optional[CacheRwMode] = CacheRwMode.RW) -> None:
        mode = ConstExpr.unwrap(mode)
        global_builder.get_ir_builder().create_asc_GlobalTensorSetL2CacheHintOp(self.to_ir(), mode, rw_mode)


class LocalTensor(BaseTensor):

    @overload
    def __init__(self) -> None:
        ...

    @overload
    def __init__(self, handle: IRHandle, dtype: DataType, shape: TensorShape) -> None:
        ...

    @overload
    def __init__(self, dtype: DataType, addr: int = 0) -> None:
        ...

    @overload
    def __init__(self, dtype: DataType, pos: Optional[Position] = Position.VECIN, \
        addr: int = 0, tile_size: int = 0):
        ...

    def __init__(self, *args, **kwargs) -> None:
        """This contructor should not be called by user"""
        dispatcher = OverloadDispatcher(__name__)

        @dispatcher.register(handle=Optional[IRHandle], dtype=DataType, shape=Optional[TensorShape])
        def _(handle: Optional[IRHandle], dtype: DataType, shape: Optional[TensorShape] = None):
            dtype = DataType.from_ir(ir.get_element_type(handle.get_type()))
            super(LocalTensor, self).__init__(dtype)
            self.handle = handle
            self.shape = self.ensure_shape(shape)

        @dispatcher.register(dtype=DataType, pos=Optional[Position], addr=RuntimeInt, tile_size=RuntimeInt)
        def _(dtype: DataType, pos: Optional[Position] = Position.VECIN, \
                addr: RuntimeInt = 0, tile_size: RuntimeInt = 0):
            super(LocalTensor, self).__init__(dtype)
            builder = global_builder.get_ir_builder()
            self.shape = None
            self.handle = builder.create_asc_LocalTensorV2Op(ir.get_local_tensor_type(dtype.to_ir()), \
                    ir.Position.symbolize(pos), _mat(addr, KnownTypes.uint32).to_ir(),\
                     _mat(tile_size, KnownTypes.uint32).to_ir())

        @dispatcher.register(dtype=DataType, addr=RuntimeInt)
        def _(dtype: DataType, addr: RuntimeInt):
            super(LocalTensor, self).__init__(dtype)
            builder = global_builder.get_ir_builder()
            self.shape = None
            self.handle = builder.create_asc_LocalTensorOp(ir.get_local_tensor_type(dtype.to_ir()), \
                _mat(addr, KnownTypes.uint32).to_ir())

        dispatcher(*args, **kwargs)

    @require_jit
    def __getitem__(self, slices: Any) -> Union[LocalTensor, RuntimeNumeric]:
        builder = global_builder.get_ir_builder()
        if isinstance(slices, RuntimeInt):
            handle = builder.create_asc_LocalTensorSubIndexOp(self.to_ir().get_type(), self.to_ir(),
                                                              _mat(slices).to_ir())
            return LocalTensor(handle, self.dtype, self.shape)
        if isinstance(slices, slice):
            if slices.step is not None or slices.stop is not None:
                raise RuntimeError("Slice operation with provided stop and step is not supported for LocalTensor")
            handle = builder.create_asc_LocalTensorSubIndexOp(self.to_ir().get_type(), self.to_ir(),
                                                              _mat(slices.start).to_ir())
            return LocalTensor(handle, self.dtype, self.shape)
        raise RuntimeError(f"Tensor subscript operation is not supported with {slices}")

    @classmethod
    def from_ir(cls, handle: IRHandle) -> LocalTensor:
        ir_type = handle.get_type()
        return cls(handle, DataType.from_ir(ir.get_element_type(ir_type)), ir.get_shape(ir_type))

    def to_ir(self) -> IRHandle:
        return self.handle

    @overload
    def set_value(self, index: int, value: Union[int, float]) -> None:
        ...

    @require_jit
    @set_tensor_docstring(tensor_name="LocalTensor", api_name="set_value")
    def set_value(self, index: RuntimeInt, value: RuntimeNumeric) -> None:
        global_builder.get_ir_builder().create_asc_LocalTensorSetValueOp(self.to_ir(),
                                                                         _mat(index, KnownTypes.uint32).to_ir(),
                                                                         _mat(value, self.dtype).to_ir())

    @overload
    def get_value(self, index: int) -> int:
        ...

    @require_jit
    @set_tensor_docstring(tensor_name="LocalTensor", api_name="get_value")
    def get_value(self, index: RuntimeInt) -> RuntimeNumeric:
        builder = global_builder.get_ir_builder()
        handle = builder.create_asc_GetValueLocalTensorOp(self.dtype.to_ir(), self.to_ir(),
                                                          _mat(index, KnownTypes.uint32).to_ir())
        return PlainValue(handle, self.dtype)

    @overload
    def set_size(self, size: int = 0) -> None:
        ...

    @require_jit
    @set_tensor_docstring(tensor_name="LocalTensor", api_name="set_size")
    def set_size(self, size: RuntimeInt = 0) -> None:
        global_builder.get_ir_builder().create_asc_LocalTensorSetSizeOp(self.to_ir(),
                                                                        _mat(size, KnownTypes.uint32).to_ir())

    @overload
    def get_size(self) -> int:
        ...

    @require_jit
    @set_tensor_docstring(tensor_name="LocalTensor", api_name="get_size")
    def get_size(self) -> RuntimeInt:
        if self.shape is None:
            builder = global_builder.get_ir_builder()
            handle = builder.create_asc_LocalTensorGetSizeOp(builder.get_i32_type(), self.to_ir())
            return PlainValue(handle)
        return itertools.accumulate(self.shape, lambda acc, next: acc * next, initial=1)

    @overload
    def set_user_tag(self, tag: int = 0) -> None:
        ...

    @require_jit
    @set_tensor_docstring(tensor_name="LocalTensor", api_name="set_user_tag")
    def set_user_tag(self, tag: RuntimeInt = 0) -> None:
        global_builder.get_ir_builder().create_asc_LocalTensorSetUserTagOp(self.to_ir(), _mat(tag).to_ir())

    @overload
    def get_user_tag(self) -> int:
        ...

    @require_jit
    @set_tensor_docstring(tensor_name="LocalTensor", api_name="get_user_tag")
    def get_user_tag(self) -> RuntimeInt:
        builder = global_builder.get_ir_builder()
        handle = builder.create_asc_LocalTensorGetUserTagOp(builder.get_i32_type(), self.to_ir())
        return PlainValue(handle)

    @require_jit
    @set_tensor_docstring(tensor_name="LocalTensor", api_name="reinterpret_cast")
    def reinterpret_cast(self, dtype: DataType) -> LocalTensor:
        if not dtype.is_numeric():
            raise RuntimeError("ReinterpretCast dtype must be integer or float")

        if self.dtype == dtype:
            return self

        tensor_type = ir.get_local_tensor_type(dtype.to_ir())
        builder = global_builder.get_ir_builder()
        handle = builder.create_asc_ReinterpretCastOp(tensor_type, self.to_ir())
        return LocalTensor(handle=handle, dtype=dtype, shape=self.shape)

    @overload
    def get_phy_addr(self) -> int:
        ...

    @overload
    def get_phy_addr(self, offset: int) -> int:
        ...

    @require_jit
    @set_tensor_docstring(tensor_name="LocalTensor", api_name="get_phy_addr")
    def get_phy_addr(self, offset: RuntimeInt = 0) -> RuntimeInt:
        builder = global_builder.get_ir_builder()
        handle = builder.create_asc_GetPhyAddrOp(builder.get_ui64_type(), self.to_ir(), \
                                                _mat(offset, KnownTypes.uint32).to_ir())
        return PlainValue(handle)

    @overload
    def get_position(self) -> int:
        ...

    @require_jit
    @set_tensor_docstring(tensor_name="LocalTensor", api_name="get_position")
    def get_position(self) -> RuntimeInt:
        builder = global_builder.get_ir_builder()
        handle = builder.create_asc_LocalTensorGetPositionOp(builder.get_i32_type(), self.to_ir())
        return PlainValue(handle)

    @overload
    def get_length(self) -> int:
        ...

    @require_jit
    @set_tensor_docstring(tensor_name="LocalTensor", api_name="get_length")
    def get_length(self) -> RuntimeInt:
        builder = global_builder.get_ir_builder()
        handle = builder.create_asc_LocalTensorGetLengthOp(builder.get_ui32_type(), self.to_ir())
        return PlainValue(handle)

    @overload
    def set_shape_info(self, shape: Tuple[int, ...]) -> None:
        ...

    @overload
    def set_shape_info(self, shape_info: ShapeInfo) -> None:
        ...

    @require_jit
    @set_tensor_docstring(tensor_name="LocalTensor", api_name="set_shape_info")
    def set_shape_info(self, shape_info: Union[ShapeInfo, Tuple[RuntimeInt, ...]]) -> None:
        builder = global_builder.get_ir_builder()
        if isinstance(shape_info, ShapeInfo):
            builder.create_asc_SetShapeInfoOp(self.to_ir(), shape_info.to_ir())
        else:
            shape_array = [_mat(value, KnownTypes.int_).to_ir() for value in shape_info]
            builder.create_asc_SetShapeInfoV2Op(self.to_ir(), shape_array)

    @require_jit
    @set_tensor_docstring(tensor_name="LocalTensor", api_name="get_shape_info")
    def get_shape_info(self) -> ShapeInfo:
        builder = global_builder.get_ir_builder()
        handle = builder.create_asc_GetShapeInfoOp(builder.get_asc_ShapeInfoType(), self.to_ir())
        return ShapeInfo(handle)

    @overload
    def set_addr_with_offset(self, src: LocalTensor, offset: int) -> None:
        ...

    @require_jit
    @set_tensor_docstring(tensor_name="LocalTensor", api_name="set_addr_with_offset")
    def set_addr_with_offset(self, src: LocalTensor, offset: RuntimeInt) -> None:
        global_builder.get_ir_builder().create_asc_LocalTensorSetAddrWithOffsetOp( \
                    self.to_ir(), src.to_ir(), _mat(offset, KnownTypes.uint32).to_ir())

    @overload
    def set_buffer_len(self, data_len: int) -> None:
        ...

    @require_jit
    @set_tensor_docstring(tensor_name="LocalTensor", api_name="set_buffer_len")
    def set_buffer_len(self, data_len: RuntimeInt) -> None:
        global_builder.get_ir_builder().create_asc_LocalTensorSetBufferLenOp( \
                    self.to_ir(), _mat(data_len, KnownTypes.uint32).to_ir())

    @require_jit
    @set_tensor_docstring(tensor_name="LocalTensor", api_name="to_file")
    def to_file(self, file_name: str) -> None:
        global_builder.get_ir_builder().create_asc_LocalTensorToFileOp(self.to_ir(), file_name)

    @overload
    def print(self, data_len: int) -> None:
        ...

    @require_jit
    @set_tensor_docstring(tensor_name="LocalTensor", api_name="print")
    def print(self, data_len: RuntimeInt) -> None:
        global_builder.get_ir_builder().create_asc_LocalTensorPrintOp( \
                    self.to_ir(), _mat(data_len, KnownTypes.uint32).to_ir())
