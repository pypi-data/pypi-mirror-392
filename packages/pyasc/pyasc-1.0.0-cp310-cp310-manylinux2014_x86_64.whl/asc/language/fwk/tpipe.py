# This program is free software, you can redistribute it and/or modify it.
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# This file is a part of the CANN Open Software.
# Licensed under CANN Open Software License Agreement Version 2.0 (the "License").
# Please refer to the License for details. You may not use this file except in compliance with the License.
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
# See LICENSE in the root of the software repository for the full text of the License.

from __future__ import annotations
from typing import ClassVar, Optional, overload

from ..._C import ir
from ..core.constexpr import ConstExpr, require_constexpr
from ..core.dtype import DataType, KnownTypes
from ..core.enums import HardEvent, Position
from ..core.ir_value import IRHandle, IRValue, PlainValue, RuntimeInt, materialize_ir_value as _mat
from ..core.tensor import LocalTensor
from ..core.types import TensorShape
from ..core.utils import OverloadDispatcher, require_jit, global_builder


class TQueBind(IRValue):

    @overload
    def __init__(self, src: Optional[Position], dst: Optional[Position] = Position.VECIN, \
                        depth: int = 0, mask: int = 0) -> None:
        ...

    @overload
    def __init__(self, handle: IRHandle) -> None:
        """This contructor should not be called by user"""
        ...

    def __init__(self, src: Optional[Position], dst: Optional[Position] = Position.VECIN, \
                    depth: Optional[int] = 0, mask: Optional[int] = 0, handle: Optional[IRHandle] = None) -> None:
        if handle is not None:
            self.handle = handle
            return
        require_constexpr(src, int, arg_name="src")
        require_constexpr(dst, int, arg_name="dst")
        require_constexpr(depth, int, arg_name="depth")
        src = ConstExpr.unwrap(src)
        dst = ConstExpr.unwrap(dst)
        depth = ConstExpr.unwrap(depth)
        builder = global_builder.get_ir_builder()
        ir_type = builder.get_quebind_type(src, dst, depth)
        self.handle = builder.create_asc_QueBindOp(ir_type)

    @classmethod
    def from_ir(cls, handle: IRHandle) -> TQue:
        return cls(handle=handle)

    def to_ir(self) -> IRHandle:
        return self.handle

    @require_jit
    def alloc_tensor(self, dtype: DataType, tensor: LocalTensor = None,
                     shape: Optional[TensorShape] = None) -> LocalTensor:
        if tensor:
            handle = global_builder.get_ir_builder().create_asc_AllocTensorInPlaceOp(tensor, self.to_ir())
            return tensor
        else:
            tensor_type = ir.get_local_tensor_type(dtype.to_ir())
            handle = global_builder.get_ir_builder().create_asc_AllocTensorOp(tensor_type, self.to_ir())
            return LocalTensor(handle=handle, dtype=dtype, shape=shape)

    @require_jit
    def free_tensor(self, tensor: LocalTensor) -> None:
        global_builder.get_ir_builder().create_asc_FreeTensorOp(self.to_ir(), tensor.to_ir())

    @require_jit
    def deque(self, dtype: DataType, tensor: LocalTensor = None, shape: Optional[TensorShape] = None) -> LocalTensor:
        builder = global_builder.get_ir_builder()
        if tensor:
            handle = builder.create_asc_DequeueTensorInPlaceOp(tensor, self.to_ir())
            return tensor
        else:
            tensor_type = ir.get_local_tensor_type(dtype.to_ir())
            handle = builder.create_asc_DequeueTensorOp(tensor_type, self.to_ir())
            return LocalTensor(handle=handle, dtype=dtype, shape=shape)

    @require_jit
    def enque(self, tensor: LocalTensor) -> None:
        builder = global_builder.get_ir_builder()
        builder.create_asc_EnqueueTensorOp(self.to_ir(), tensor.to_ir())

    @require_jit
    def vacant_in_que(self) -> bool:
        builder = global_builder.get_ir_builder()
        handle = builder.create_asc_TQueBindVacantInQueOp(builder.get_i32_type(), self.to_ir())
        return PlainValue(handle=handle)

    @require_jit
    def has_tensor_in_que(self) -> bool:
        builder = global_builder.get_ir_builder()
        handle = builder.create_asc_TQueBindHasTensorInQueOp(builder.get_i32_type(), self.to_ir())
        return PlainValue(handle=handle)

    @require_jit
    def get_tensor_count_in_que(self) -> RuntimeInt:
        builder = global_builder.get_ir_builder()
        handle = builder.create_asc_TQueBindGetTensorCountInQueOp(builder.get_i32_type(), self.to_ir())
        return PlainValue(handle=handle)

    @require_jit
    def has_idle_buffer(self) -> bool:
        builder = global_builder.get_ir_builder()
        handle = builder.create_asc_TQueBindHasIdleBufferOp(builder.get_i32_type(), self.to_ir())
        return PlainValue(handle=handle)

    @require_jit
    def free_all_event(self) -> None:
        builder = global_builder.get_ir_builder()
        builder.create_asc_TQueBindFreeAllEventOp(self.to_ir())

    @require_jit
    def init_buf_handle(self, buf_pool: TBufPool, index: RuntimeInt, buf_handle: TBufHandle, cur_pool_addr: TBufHandle,
                        len: RuntimeInt) -> None:
        builder = global_builder.get_ir_builder()
        builder.create_asc_TQueBindInitBufHandleOp(self.to_ir(), buf_pool.to_ir(),
                                           _mat(index, KnownTypes.uint32).to_ir(), buf_handle.to_ir(),
                                           cur_pool_addr.to_ir(),
                                           _mat(len, KnownTypes.uint32).to_ir())

    @require_jit
    def init_start_buf_handle(self, start_buf_handle: TBufHandle, num: RuntimeInt, len: RuntimeInt) -> None:
        builder = global_builder.get_ir_builder()
        builder.create_asc_TQueBindInitStartBufHandleOp(self.to_ir(), start_buf_handle.to_ir(),
                                                _mat(num, KnownTypes.uint8).to_ir(),
                                                _mat(len, KnownTypes.uint32).to_ir())


class TBuf(TQueBind):

    @overload
    def __init__(self, pos: Position) -> None:
        ...

    @overload
    def __init__(self, handle: IRHandle) -> None:
        """This contructor should not be called by user"""
        ...

    def __init__(self, pos: Optional[Position] = None, handle: Optional[IRHandle] = None) -> None:
        if handle is not None:
            self.handle = handle
            return
        super().__init__(pos, pos, 0, 0)
        require_constexpr(pos, int, arg_name="pos")
        pos = ConstExpr.unwrap(pos)
        builder = global_builder.get_ir_builder()
        ir_type = builder.get_buffer_type(pos)
        self.handle = builder.create_asc_BufferOp(ir_type)

    @classmethod
    def from_ir(cls, handle: IRHandle) -> TBuf:
        return cls(handle=handle)

    def to_ir(self) -> IRHandle:
        return self.handle

    @overload
    def get(self, dtype: DataType, shape: Optional[TensorShape] = None) -> LocalTensor:
        ...

    @overload
    def get(self, dtype: DataType, len: int = None, shape: Optional[TensorShape] = None) -> LocalTensor:
        ...

    @require_jit
    def get(self, dtype: DataType, len: RuntimeInt = None, shape: Optional[TensorShape] = None) -> LocalTensor:
        builder = global_builder.get_ir_builder()
        tensor_type = ir.get_local_tensor_type(dtype.to_ir())

        if len:
            handle = builder.create_asc_GetTensorOp(tensor_type, self.to_ir(), _mat(len, KnownTypes.uint32).to_ir())
        else:
            handle = builder.create_asc_GetTensorOp(tensor_type, self.to_ir())
        return LocalTensor(handle=handle, dtype=dtype, shape=shape)

    @overload
    def get_with_offset(self, dtype: DataType, size: int = 0, buf_offset: int = 0,
                        shape: Optional[TensorShape] = None) -> LocalTensor:
        ...

    @require_jit
    def get_with_offset(self, dtype: DataType, size: RuntimeInt = 0, buf_offset: RuntimeInt = 0,
                        shape: Optional[TensorShape] = None) -> LocalTensor:
        if buf_offset % 32 != 0:
            raise ValueError("buf_offset must be align to 32B.")

        tensor_type = ir.get_local_tensor_type(dtype.to_ir())
        builder = global_builder.get_ir_builder()
        handle = builder.create_asc_TBufGetWithOffsetOp(tensor_type, self.to_ir(), \
                            _mat(size, KnownTypes.uint32).to_ir(), _mat(buf_offset, KnownTypes.uint32).to_ir())
        return LocalTensor(handle=handle, dtype=dtype, shape=shape)


class TBufHandle(IRValue):

    def __init__(self, handle: IRHandle):
        """This contructor should not be called by user"""
        self.handle = handle
        self.dtype = KnownTypes.uint8

    @classmethod
    def from_ir(cls, handle: IRHandle) -> TBufHandle:
        return TBufHandle(handle)

    def to_ir(self) -> IRHandle:
        return self.handle


class TBufPool(IRValue):

    @overload
    def __init__(self, pos: Optional[Position], buf_id_size: int) -> None:
        ...

    @overload
    def __init__(self, handle: IRHandle) -> None:
        """This contructor should not be called by user"""
        ...

    def __init__(self, pos: Optional[Position] = None, buf_id_size: RuntimeInt = 4,
                 handle: Optional[IRHandle] = None) -> None:
        if handle is not None:
            self.handle = handle
            return
        require_constexpr(pos, int, arg_name="pos")
        pos = ConstExpr.unwrap(pos)
        builder = global_builder.get_ir_builder()
        self.handle = builder.create_asc_TBufPoolOp(pos, _mat(buf_id_size, KnownTypes.uint32).to_ir())
    
    @classmethod
    def from_ir(cls, handle: IRHandle) -> TBufPool:
        return cls(handle=handle)

    def to_ir(self) -> IRHandle:
        return self.handle

    @overload
    def init_buf_pool(self, buf_pool: TBufPool, len: int = 0, share_buf: TBufPool = None) -> None:
        ...

    @require_jit
    def init_buf_pool(self, buf_pool: TBufPool, len: RuntimeInt = 0, share_buf: TBufPool = None) -> None:
        builder = global_builder.get_ir_builder()
        if share_buf:
            builder.create_asc_BufPoolInitBufferPoolOp(self.to_ir, buf_pool.to_ir,
                                                       _mat(len, KnownTypes.uint32).to_ir(), share_buf.to_ir())
        else:
            builder.create_asc_BufPoolInitBufferPoolOp(self.to_ir, buf_pool.to_ir, _mat(len, KnownTypes.uint32).to_ir())

    @overload
    def init_buffer(self, que: TQue, num: int = 0, len: int = 0) -> None:
        ...

    @overload
    def init_buffer(self, buf: TBuf, num: int = 0) -> None:
        ...

    @require_jit
    def init_buffer(self, *args, **kwargs) -> None:
        dispatcher = OverloadDispatcher(__name__)

        @dispatcher.register(que=TQue, num=RuntimeInt, len=RuntimeInt)
        def _(que: TQue, num: RuntimeInt = 0, len: RuntimeInt = 0):
            global_builder.get_ir_builder().create_asc_BufPoolInitQueueOp(self.to_ir(), que.to_ir(),
                                                                          _mat(num, KnownTypes.int_).to_ir(),
                                                                          _mat(len, KnownTypes.int_).to_ir())

        @dispatcher.register(buf=TBuf, num=RuntimeInt)
        def _(buf: TBuf, num: RuntimeInt = 0):
            global_builder.get_ir_builder().create_asc_BufPoolInitBufferOp(self.to_ir(), buf.to_ir(),
                                                                           _mat(num, KnownTypes.int_).to_ir())

        dispatcher(*args, **kwargs)

    @require_jit
    def reset(self) -> None:
        global_builder.get_ir_builder().create_asc_BufPoolResetOp(self.to_ir())


class TPipe(IRValue):

    @overload
    def __init__(self) -> None:
        ...

    @overload
    def __init__(self, handle: IRHandle) -> None:
        """This contructor should not be called by user"""
        ...

    def __init__(self, handle: Optional[IRHandle] = None) -> None:
        if handle is not None:
            self.handle = handle
            return
        self.handle = global_builder.get_ir_builder().create_asc_PipeOp()
        TPipeManager.set(self)

    @classmethod
    def from_ir(cls, handle: IRHandle) -> TPipe:
        return cls(handle=handle)

    def to_ir(self) -> IRHandle:
        return self.handle

    @overload
    def init_buffer(self, que: TQue, num: int = 0, len: int = 0) -> None:
        ...

    @overload
    def init_buffer(self, buf: TBuf, num: int = 0) -> None:
        ...

    @require_jit
    def init_buffer(self, *args, **kwargs) -> None:
        dispatcher = OverloadDispatcher(__name__)

        @dispatcher.register(que=TQue, num=RuntimeInt, len=RuntimeInt)
        def _(que: TQue, num: RuntimeInt = 0, len: RuntimeInt = 0):
            global_builder.get_ir_builder().create_asc_InitQueueOp(self.to_ir(), que.to_ir(),
                                                                   _mat(num, KnownTypes.int_).to_ir(),
                                                                   _mat(len, KnownTypes.int_).to_ir())

        @dispatcher.register(buf=TBuf, num=RuntimeInt)
        def _(buf: TBuf, num: RuntimeInt = 0):
            global_builder.get_ir_builder().create_asc_InitBufferOp(self.to_ir(), buf.to_ir(),
                                                                    _mat(num, KnownTypes.int_).to_ir())

        dispatcher(*args, **kwargs)

    @require_jit
    def init(self) -> None:
        global_builder.get_ir_builder().create_asc_TPipeInitOp(self.to_ir())

    @require_jit
    def destroy(self) -> None:
        global_builder.get_ir_builder().create_asc_TPipeDestroyOp(self.to_ir())

    @require_jit
    def reset(self) -> None:
        global_builder.get_ir_builder().create_asc_TPipeResetOp(self.to_ir())

    @overload
    def alloc_event_id(self, event: HardEvent = HardEvent.V_S) -> int:
        ...

    @require_jit
    def alloc_event_id(self, event: HardEvent = HardEvent.V_S) -> RuntimeInt:
        return PlainValue(global_builder.get_ir_builder() \
                        .create_asc_TPipeAllocEventIDOp(KnownTypes.int_.to_ir(), self.to_ir(), event))

    @overload
    def release_event_id(self, id: int, event: HardEvent = HardEvent.V_S) -> None:
        ...

    @require_jit
    def release_event_id(self, id: RuntimeInt, event: HardEvent = HardEvent.V_S) -> None:
        global_builder.get_ir_builder() \
                      .create_asc_TPipeReleaseEventIDOp(self.to_ir(), _mat(id, KnownTypes.int_).to_ir(), event)

    @overload
    def fetch_event_id(self, event: HardEvent = HardEvent.V_S) -> int:
        ...

    @require_jit
    def fetch_event_id(self, event: HardEvent = HardEvent.V_S) -> RuntimeInt:
        return PlainValue(global_builder.get_ir_builder() \
                        .create_asc_TPipeFetchEventIDOp(KnownTypes.int_.to_ir(), self.to_ir(), event))

    @overload
    def get_base_addr(self, logic_pos: Optional[Position] = None) -> int:
        ...

    @require_jit
    def get_base_addr(self, logic_pos: Optional[Position] = None) -> RuntimeInt:
        require_constexpr(logic_pos, int, arg_name="logic_pos")
        logic_pos = ConstExpr.unwrap(logic_pos)
        builder = global_builder.get_ir_builder()
        return PlainValue(builder.create_asc_TPipeGetBaseAddrOp(builder.get_i32_type(), self.to_ir(), \
                            ir.Position.symbolize(logic_pos)))

    @overload
    def init_buf_pool(self, buf_pool: TBufPool, len: int = 0, share_buf: TBufPool = None) -> None:
        ...

    @require_jit
    def init_buf_pool(self, buf_pool: TBufPool, len: RuntimeInt = 0, share_buf: TBufPool = None) -> None:
        builder = global_builder.get_ir_builder()
        if share_buf:
            builder.create_asc_InitBufferPoolOp(self.to_ir, buf_pool.to_ir,
                                                _mat(len, KnownTypes.uint32).to_ir(), share_buf.to_ir())
        else:
            builder.create_asc_InitBufferPoolOp(self.to_ir, buf_pool.to_ir, _mat(len, KnownTypes.uint32).to_ir())


class TPipeManager:
    instance: ClassVar[Optional[TPipe]] = None

    @classmethod
    def get(cls) -> TPipe:
        if cls.instance is None:
            raise RuntimeError("TPipe instance is not initialized, use TPipe() to create it")
        return cls.instance

    @classmethod
    def set(cls, pipe: TPipe) -> None:
        if cls.instance is not None:
            raise RuntimeError("TPipe instance is already created, use get_tpipe_ptr() to obtain it")
        cls.instance = pipe
        global_builder.on_teardown(cls.reset)

    @classmethod
    def reset(cls) -> None:
        cls.instance = None


def get_tpipe_ptr() -> TPipe:
    return TPipeManager.get()


class TQue(TQueBind):

    @overload
    def __init__(self, pos: Position = Position.VECIN, depth: int = 1) -> None:
        ...

    @overload
    def __init__(self, handle: IRHandle) -> None:
        """This contructor should not be called by user"""
        ...

    def __init__(self, pos: Optional[Position] = Position.VECIN, depth: Optional[int] = None, mask: Optional[int] = 0,
                 handle: Optional[IRHandle] = None) -> None:
        if handle is not None:
            self.handle = handle
            return
        require_constexpr(pos, int, arg_name="pos")
        require_constexpr(depth, int, arg_name="depth")
        pos = ConstExpr.unwrap(pos)
        depth = ConstExpr.unwrap(depth)
        builder = global_builder.get_ir_builder()
        ir_type = builder.get_queue_type(pos, depth)
        self.handle = builder.create_asc_QueueOp(ir_type)
        super().__init__(pos, pos, depth, mask, self.handle)

    @classmethod
    def from_ir(cls, handle: IRHandle) -> TQue:
        return cls(handle=handle)

    def to_ir(self) -> IRHandle:
        return self.handle

    @require_jit
    def vacant_in_que(self) -> bool:
        builder = global_builder.get_ir_builder()
        handle = builder.create_asc_TQueVacantInQueOp(builder.get_i32_type(), self.to_ir())
        return PlainValue(handle=handle)

    @require_jit
    def has_tensor_in_que(self) -> bool:
        builder = global_builder.get_ir_builder()
        handle = builder.create_asc_TQueHasTensorInQueOp(builder.get_i32_type(), self.to_ir())
        return PlainValue(handle=handle)

    @require_jit
    def get_tensor_count_in_que(self) -> RuntimeInt:
        builder = global_builder.get_ir_builder()
        handle = builder.create_asc_TQueGetTensorCountInQueOp(builder.get_i32_type(), self.to_ir())
        return PlainValue(handle=handle)

    @require_jit
    def has_idle_buffer(self) -> bool:
        builder = global_builder.get_ir_builder()
        handle = builder.create_asc_TQueHasIdleBufferOp(builder.get_i32_type(), self.to_ir())
        return PlainValue(handle=handle)
