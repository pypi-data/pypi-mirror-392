# This program is free software, you can redistribute it and/or modify it.
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# This file is a part of the CANN Open Software.
# Licensed under CANN Open Software License Agreement Version 2.0 (the "License").
# Please refer to the License for details. You may not use this file except in compliance with the License.
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
# See LICENSE in the root of the software repository for the full text of the License.

from typing import overload

from ..._C import ir
from ..core.dtype import DataType, KnownTypes
from ..core.enums import HardEvent, PipeID, Position
from ..core.ir_value import GlobalAddress, PlainValue, RuntimeInt, materialize_ir_value as _mat
from ..core.tensor import LocalTensor
from ..core.utils import require_jit, global_builder


@require_jit
def ffts_cross_core_sync(pipe: PipeID, config: int) -> None:
    config = _mat(config, KnownTypes.int64)
    global_builder.get_ir_builder().create_asc_FftsCrossCoreSyncOp(pipe, config.to_ir())


@require_jit
def get_sys_workspace() -> GlobalAddress:
    builder = global_builder.get_ir_builder()
    ir_type = ir.get_memref_type(builder.get_i8_type(), [ir.dynshape], ir.AddressSpace.gm)
    return GlobalAddress(builder.create_asc_GetSysWorkspacePtrOp(ir_type), KnownTypes.int8)


@require_jit
def is_cube_core() -> PlainValue:
    builder = global_builder.get_ir_builder()
    handle = builder.create_asc_AscendIsAICOp(builder.get_i1_type())
    return PlainValue(handle)


@require_jit
def is_vector_core() -> PlainValue:
    builder = global_builder.get_ir_builder()
    handle = builder.create_asc_AscendIsAIVOp(builder.get_i1_type())
    return PlainValue(handle)


@require_jit
def pipe_barrier(pipe: PipeID) -> None:
    global_builder.get_ir_builder().create_asc_PipeBarrierOp(pipe)


@require_jit
def pop_stack_buffer(dtype: DataType, position: Position = Position.VECCALC) -> LocalTensor:
    builder = global_builder.get_ir_builder()
    handle = builder.create_asc_LocalTensorOp(ir.get_local_tensor_type(dtype.to_ir()))
    tensor = LocalTensor(handle, dtype, shape=None)
    builder.create_asc_PopStackBufferOp(ir.Position.symbolize(position), tensor.to_ir())
    return tensor


@require_jit
def set_ffts_base_addr(ffts_address: GlobalAddress) -> None:
    global_builder.get_ir_builder().create_asc_SetFftsBaseAddrOp(ffts_address.to_ir())


@require_jit
def set_sys_workspace_force(workspace: GlobalAddress) -> None:
    global_builder.get_ir_builder().create_asc_SetSysWorkspaceForceOp(workspace.to_ir())


@overload
def set_flag(event: HardEvent, event_id: int = 0) -> None:
    ...


@require_jit
def set_flag(event: HardEvent, event_id: RuntimeInt = 0) -> None:
    event_id = _mat(event_id).to_ir()
    global_builder.get_ir_builder().create_asc_SetFlagOp(event, event_id)


@overload
def wait_flag(event: HardEvent, event_id: int = 0) -> None:
    ...


@require_jit
def wait_flag(event: HardEvent, event_id: RuntimeInt = 0) -> None:
    event_id = _mat(event_id).to_ir()
    global_builder.get_ir_builder().create_asc_WaitFlagOp(event, event_id)
