# This program is free software, you can redistribute it and/or modify it.
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# This file is a part of the CANN Open Software.
# Licensed under CANN Open Software License Agreement Version 2.0 (the "License").
# Please refer to the License for details. You may not use this file except in compliance with the License.
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
# See LICENSE in the root of the software repository for the full text of the License.

from __future__ import annotations
from typing import Any, Iterable, Optional, Tuple, Union, overload

from ..._C import ir
from ...common.compat import isinstance
from .array import Array
from .dtype import KnownTypes
from .enums import BlockMode, DataFormat, DeqScale, pad_t
from .ir_value import IRHandle, IRValue, PlainValue, \
                            RuntimeBool, RuntimeInt, RuntimeNumeric, materialize_ir_value as _mat
from .utils import require_jit, global_builder
from .properties import property, ONE_BLK_SIZE


class BinaryRepeatParams(IRValue):

    @overload
    def __init__(self, dst_blk_stride: int = 1, src0_blk_stride: int = 1, src1_blk_stride: int = 1,
                 dst_rep_stride: int = 8, src0_rep_stride: int = 8, src1_rep_stride: int = 8) -> None:
        ...

    @overload
    def __init__(self, handle: IRHandle) -> None:
        """This contructor should not be called by user"""
        ...

    def __init__(self, dst_blk_stride: RuntimeInt = 1, src0_blk_stride: RuntimeInt = 1, src1_blk_stride: RuntimeInt = 1,
                 dst_rep_stride: RuntimeInt = 8, src0_rep_stride: RuntimeInt = 8, src1_rep_stride: RuntimeInt = 8,
                 handle: Optional[IRHandle] = None) -> None:
        if handle is not None:
            self.handle = handle
            return
        builder = global_builder.get_ir_builder()
        self.handle = builder.create_asc_ConstructOp(
            builder.get_asc_BinaryRepeatParamsType(),
            [
                _mat(dst_blk_stride).to_ir(),
                _mat(src0_blk_stride).to_ir(),
                _mat(src1_blk_stride).to_ir(),
                _mat(dst_rep_stride).to_ir(),
                _mat(src0_rep_stride).to_ir(),
                _mat(src1_rep_stride).to_ir(),
            ],
            builder.get_type_array_attr([builder.get_ui8_type()] * 6),
        )

    @classmethod
    def from_ir(cls, handle: IRHandle) -> BinaryRepeatParams:
        return cls(handle=handle)

    def to_ir(self) -> IRHandle:
        return self.handle


class DataCopyParams(IRValue):

    @overload
    def __init__(self, block_count: int = 1, block_len: int = 0, src_stride: int = 0, dst_stride: int = 0) -> None:
        ...

    @overload
    def __init__(self, handle: IRHandle) -> None:
        """This contructor should not be called by user"""
        ...

    def __init__(self, block_count: RuntimeInt = 1, block_len: RuntimeInt = 0, src_stride: RuntimeInt = 0,
                 dst_stride: RuntimeInt = 0, handle: Optional[IRHandle] = None) -> None:
        if handle is not None:
            self.handle = handle
            return
        builder = global_builder.get_ir_builder()
        self.handle = builder.create_asc_ConstructOp(
            builder.get_asc_DataCopyParamsType(),
            [
                _mat(block_count).to_ir(),
                _mat(block_len).to_ir(),
                _mat(src_stride).to_ir(),
                _mat(dst_stride).to_ir(),
            ],
            builder.get_type_array_attr([builder.get_ui16_type()] * 4),
        )

    @classmethod
    def from_ir(cls, handle: IRHandle) -> DataCopyParams:
        return cls(handle=handle)

    def to_ir(self) -> IRHandle:
        return self.handle


class DataCopyEnhancedParams(IRValue):

    @overload
    def __init__(self, block_mode: BlockMode = BlockMode.BLOCK_MODE_NORMAL, deq_scale: DeqScale = DeqScale.DEQ_NONE,
                 deq_value_in: int = 0, sid_store_mode_in: int = 0, is_relu_in: bool = False,
                 pad_mode_in: pad_t = pad_t.PAD_NONE, pad_value_in: int = 0) -> None:
        ...

    @overload
    def __init__(self, handle: IRHandle) -> None:
        """This contructor should not be called by user"""
        ...

    def __init__(self, block_mode: BlockMode = BlockMode.BLOCK_MODE_NORMAL, deq_scale: DeqScale = DeqScale.DEQ_NONE,
                 deq_value_in: RuntimeInt = 0, sid_store_mode_in: RuntimeInt = 0, is_relu_in: RuntimeBool = False,
                 pad_mode_in: pad_t = pad_t.PAD_NONE, pad_value_in: RuntimeInt = 0,
                 handle: Optional[IRHandle] = None) -> None:
        if handle is not None:
            self.handle = handle
            return
        builder = global_builder.get_ir_builder()
        self.handle = builder.create_asc_ConstructOp(
            builder.get_asc_DataCopyEnhancedParamsType(),
            [
                _mat(block_mode).to_ir(),
                _mat(deq_scale).to_ir(),
                _mat(deq_value_in).to_ir(),
                _mat(sid_store_mode_in).to_ir(),
                _mat(is_relu_in).to_ir(),
                _mat(pad_mode_in).to_ir(),
                _mat(pad_value_in).to_ir(),
            ],
            builder.get_type_array_attr([
                builder.get_asc_BlockModeType(),
                builder.get_asc_DeqScaleType(),
                builder.get_ui64_type(),
                builder.get_ui8_type(),
                builder.get_i1_type(),
                builder.get_asc_PadType(),
                builder.get_ui64_type()
            ]),
        )

    @classmethod
    def from_ir(cls, handle: IRHandle) -> DataCopyEnhancedParams:
        return cls(handle=handle)

    def to_ir(self) -> IRHandle:
        return self.handle


class ShapeInfo(IRValue):

    @overload
    def __init__(self) -> None:
        ...

    @overload
    def __init__(self, shape: Array, original_shape: Optional[Array] = None,
                 data_format: DataFormat = DataFormat.ND) -> None:
        ...

    @overload
    def __init__(self, handle: IRHandle) -> None:
        """This contructor should not be called by user"""
        ...

    def __init__(self, shape: Optional[Array] = None, original_shape: Optional[Array] = None,
                 data_format: Optional[DataFormat] = None, handle: Optional[IRHandle] = None) -> None:
        if handle is not None:
            self.handle = handle
            return
        operands = []
        types = []
        builder = global_builder.get_ir_builder()
        if shape is not None:
            builder.set_emit_as_unsigned(shape.to_ir().get_defining_op())
            shape_len = _mat(len(shape), KnownTypes.int8).to_ir()
            operands += [shape_len, shape.to_ir()]
            ir_memref = ir.get_unranked_memref_type(builder.get_ui32_type())
            types += [builder.get_ui8_type(), ir_memref]
            if original_shape is not None:
                builder.set_emit_as_unsigned(original_shape.to_ir().get_defining_op())
                orig_shape_len = _mat(len(original_shape), KnownTypes.int8).to_ir()
                operands += [orig_shape_len, original_shape.to_ir()]
                types += [builder.get_ui8_type(), ir_memref]
            data_format = DataFormat.ND if data_format is None else data_format
            operands.append(_mat(data_format, KnownTypes.int8).to_ir())
            types.append(builder.get_asc_DataFormatType())
        types_attr = builder.get_type_array_attr(types)
        self.handle = builder.create_asc_ConstructOp(builder.get_asc_ShapeInfoType(), operands, types_attr)

    @classmethod
    def from_ir(cls, handle: IRHandle) -> ShapeInfo:
        return cls(handle=handle)

    @overload
    def shape(self, dim: int) -> int:
        ...

    @require_jit
    def shape(self, dim: RuntimeInt) -> RuntimeInt:
        dim = _mat(dim).to_ir()
        builder = global_builder.get_ir_builder()
        handle = builder.create_asc_ShapeInfoShapeOp(builder.get_i32_type(), self.to_ir(), dim)
        return PlainValue(handle)

    @overload
    def original_shape(self, dim: int) -> int:
        ...

    @require_jit
    def original_shape(self, dim: RuntimeInt) -> RuntimeInt:
        dim = _mat(dim).to_ir()
        builder = global_builder.get_ir_builder()
        handle = builder.create_asc_ShapeInfoOriginalShapeOp(builder.get_i32_type(), self.to_ir(), dim)
        return PlainValue(handle)

    def to_ir(self) -> IRHandle:
        return self.handle


class SliceInfo(IRValue):

    @overload
    def __init__(self, start_index: int = 0, end_index: int = None, stride: int = 0, burst_len: int = None,
                 shape_value: int = 0) -> None:
        ...

    @overload
    def __init__(self, handle: IRHandle) -> None:
        """This contructor should not be called by user"""
        ...

    def __init__(self, start_index: RuntimeInt = 0, end_index: RuntimeInt = None, stride: RuntimeInt = 0,
                 burst_len: RuntimeInt = None, shape_value: RuntimeInt = 0, handle: Optional[IRHandle] = None) -> None:

        builder = global_builder.get_ir_builder()

        if handle is not None:
            self.handle = handle
            return

        if not end_index:
            end_index = property(prop=ONE_BLK_SIZE, builder=builder).__sub__(1, builder=builder)
        if not burst_len:
            burst_len = property(prop=ONE_BLK_SIZE, builder=builder)

        self.handle = builder.create_asc_ConstructOp(
            builder.get_asc_SliceInfoType(),
            [
                _mat(start_index).to_ir(),
                _mat(end_index).to_ir(),
                _mat(stride).to_ir(),
                _mat(burst_len).to_ir(),
                _mat(shape_value).to_ir(),
            ],
            builder.get_type_array_attr([builder.get_ui32_type()] * 5),
        )

    @require_jit
    def __getitem__(self, slices: Any) -> Union[SliceInfo, RuntimeNumeric]:
        builder = global_builder.get_ir_builder()

        if isinstance(slices, RuntimeInt):
            handle = builder.create_asc_GetValueSliceInfoOp(self.dtype.to_ir(), self.to_ir(), _mat(slices).to_ir())
            return PlainValue(handle, self.dtype)
        if isinstance(slices, slice):
            if slices.step is not None or slices.stop is not None:
                raise RuntimeError("Slice operation with provided stop and step is not supported for SliceInfo")
            handle = builder.create_asc_SliceInfoSubIndexOp(self.to_ir().get_type(), self.to_ir(),
                                                            _mat(slices.start).to_ir())
            return SliceInfo(handle=handle)
        raise RuntimeError(f"SliceInfo subscript operation is not supported with {slices}")

    @classmethod
    def from_ir(cls, handle: IRHandle) -> SliceInfo:
        return cls(handle=handle)

    def to_ir(self) -> IRHandle:
        return self.handle


class TensorShape(Tuple[int, ...]):

    @overload
    def __new__(cls):
        ...

    @overload
    def __new__(cls, size: int, /):
        ...

    @overload
    def __new__(cls, shape: Iterable[int], /):
        ...

    @overload
    def __new__(cls, shape: TensorShape, /):
        ...

    @overload
    def __new__(cls, *dims: int):
        ...

    @overload
    def __new__(cls, empty: None, /):
        ...

    def __new__(cls, *args):
        num_args = len(args)
        if num_args == 0:
            return cls.new_impl(tuple())
        if num_args > 1:
            return cls.new_impl(tuple(cls.as_int(a) for a in args))

        if num_args != 1:
            raise ValueError("num_args must be 1")
        arg = args[0]
        if arg is None:
            return cls.new_impl(tuple())
        if isinstance(arg, TensorShape):
            return arg
        if isinstance(arg, Iterable):
            return cls.new_impl(tuple(cls.as_int(a) for a in arg))
        # single value
        return cls.new_impl((cls.as_int(arg), ))

    @staticmethod
    def as_int(value: Any) -> Optional[int]:
        try:
            return int(value)
        except Exception:
            raise TypeError(f"TensorShape accepts values convertible to int, got {value.__class__.__name__}")

    @classmethod
    def new_impl(cls, t: Tuple[int, ...]):
        return super(__class__, cls).__new__(cls, t)


class UnaryRepeatParams(IRValue):

    @overload
    def __init__(self, block_count: int = 1, block_len: int = 0, src_stride: int = 0, dst_stride: int = 0) -> None:
        ...

    @overload
    def __init__(self, handle: IRHandle) -> None:
        """This contructor should not be called by user"""
        ...

    def __init__(self, dst_blk_stride: RuntimeInt = 1, src_blk_stride: RuntimeInt = 1, dst_rep_stride: RuntimeInt = 8,
                 src_rep_stride: RuntimeInt = 8, handle: Optional[IRHandle] = None) -> None:
        if handle is not None:
            self.handle = handle
            return
        builder = global_builder.get_ir_builder()
        self.handle = builder.create_asc_ConstructOp(
            builder.get_asc_UnaryRepeatParamsType(),
            [
                _mat(dst_blk_stride).to_ir(),
                _mat(src_blk_stride).to_ir(),
                _mat(dst_rep_stride).to_ir(),
                _mat(src_rep_stride).to_ir(),
            ],
            builder.get_type_array_attr([
                builder.get_ui16_type(),
                builder.get_ui16_type(),
                builder.get_ui8_type(),
                builder.get_ui8_type(),
            ]),
        )

    @classmethod
    def from_ir(cls, handle: IRHandle) -> UnaryRepeatParams:
        return cls(handle=handle)

    def to_ir(self) -> IRHandle:
        return self.handle
