# This program is free software, you can redistribute it and/or modify it.
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# This file is a part of the CANN Open Software.
# Licensed under CANN Open Software License Agreement Version 2.0 (the "License").
# Please refer to the License for details. You may not use this file except in compliance with the License.
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
# See LICENSE in the root of the software repository for the full text of the License.

from __future__ import annotations

from typing import Optional, overload

from ..core.dtype import KnownTypes as KT
from ..core.enums import BatchMode, IterateMode, IterateOrder, ScheduleType
from ..core.ir_value import IRHandle, IRValue, materialize_ir_value as _mat
from ..core.struct import Field, Struct
from ..core.utils import global_builder


class MatmulConfig(Struct):
    do_norm = Field(dtype=KT.int1, default=False, name="doNorm")
    do_basic_block = Field(dtype=KT.int1, default=False, name="doBasicBlock")
    do_multi_data_load = Field(dtype=KT.int1, default=False, name="doMultiDataLoad")
    basic_m = Field(dtype=KT.uint32, default=0, name="basicM")
    basic_n = Field(dtype=KT.uint32, default=0, name="basicN")
    basic_k = Field(dtype=KT.uint32, default=0, name="basicK")
    intrinsics_check = Field(dtype=KT.int1, default=False, name="intrinsicsCheck")
    is_n_batch = Field(dtype=KT.int1, default=False, name="isNBatch")
    en_vec_nd2nz = Field(dtype=KT.int1, default=False, name="enVecND2NZ")
    do_special_basic_block = Field(dtype=KT.int1, default=False, name="doSpecialBasicBlock")
    do_mte2_preload = Field(dtype=KT.uint32, default=0, name="doMTE2Preload")
    single_core_m = Field(dtype=KT.uint32, default=0, name="singleCoreM")
    single_core_n = Field(dtype=KT.uint32, default=0, name="singleCoreN")
    single_core_k = Field(dtype=KT.uint32, default=0, name="singleCoreK")
    step_m = Field(dtype=KT.uint32, default=0, name="stepM")
    step_n = Field(dtype=KT.uint32, default=0, name="stepN")
    base_mn = Field(dtype=KT.uint32, default=0, name="baseMN")
    single_core_mn = Field(dtype=KT.uint32, default=0, name="singleCoreMN")
    en_unit_flag = Field(dtype=KT.int1, default=False, name="enUnitFlag")
    is_per_tensor = Field(dtype=KT.int1, default=False, name="isPerTensor")
    has_anti_quant_offset = Field(dtype=KT.int1, default=False, name="hasAntiQuantOffset")
    do_ibshare_norm = Field(dtype=KT.int1, default=False, name="doIBshareNorm")
    do_special_mdl = Field(dtype=KT.int1, default=False, name="doSpecialMDL")
    enable_init = Field(dtype=KT.int1, default=False, name="enableInit")
    batch_mode = Field(dtype=KT.uint32, default=BatchMode.NONE.value, name="batchMode")
    enable_end = Field(dtype=KT.int1, default=False, name="enableEnd")
    enable_get_tensor_c = Field(dtype=KT.int1, default=False, name="enableGetTensorC")
    enable_set_org_shape = Field(dtype=KT.int1, default=False, name="enableSetOrgShape")
    enable_set_bias = Field(dtype=KT.int1, default=False, name="enableSetBias")
    enable_set_tail = Field(dtype=KT.int1, default=False, name="enableSetTail")
    enable_quant_vector = Field(dtype=KT.int1, default=False, name="enableQuantVector")
    enable_set_define_data = Field(dtype=KT.int1, default=False, name="enableSetDefineData")
    iterate_mode = Field(dtype=KT.uint8, default=IterateMode.ITERATE_MODE_DEFAULT, name="iterateMode")
    enable_reuse = Field(dtype=KT.int1, default=True, name="enableReuse")
    enable_ub_reuse = Field(dtype=KT.int1, default=False, name="enableUBReuse")
    enable_l1_cache_ub = Field(dtype=KT.int1, default=False, name="enableL1CacheUB")
    intra_block_part_sum = Field(dtype=KT.int1, default=False, name="intraBlockPartSum")
    iterate_order = Field(dtype=KT.uint32, default=IterateOrder.UNDEF.value, name="iterateOrder")
    schedule_type = Field(dtype=KT.uint32, default=ScheduleType.INNER_PRODUCT.value, name="scheduleType")
    enable_double_cache = Field(dtype=KT.int1, default=0, name="enableDoubleCache")
    is_bias_batch = Field(dtype=KT.int1, default=True, name="isBiasBatch")
    enable_static_pad_zeros = Field(dtype=KT.int1, default=False, name="enableStaticPadZeros")
    is_partial_output = Field(dtype=KT.int1, default=False, name="isPartialOutput")
    enable_mix_dual_master = Field(dtype=KT.int1, default=False, name="enableMixDualMaster")
    is_a2b2_shared = Field(dtype=KT.int1, default=False, name="isA2B2Shared")
    is_enable_channel_split = Field(dtype=KT.int1, default=False, name="isEnableChannelSplit")
    enable_kdim_reorder_load = Field(dtype=KT.int1, default=False, name="enableKdimReorderLoad")
    is_co1_shared = Field(dtype=KT.int1, default=False, name="isCO1Shared")
    shared_co1_buffer_size = Field(dtype=KT.uint32, default=64 * 1024, name="sharedCO1BufferSize")
    enable_l1_bank_conflict_optimise = Field(dtype=KT.int1, default=0, name="enableL1BankConflictOptimise")

    @classmethod
    def get_ir_type(cls):
        return global_builder.get_ir_builder().get_asc_MatmulConfigType()


class QuantConfig(IRValue):

    @overload
    def __init__(self, calc_count: int = 0, offset_count: int = 0, scale_count: int = 0,
                 work_local_size: int = 0) -> None:
        ...

    @overload
    def __init__(self, handle: IRHandle) -> None:
        """This contructor should not be called by user"""
        ...

    def __init__(self, calc_count: int = 0, offset_count: int = 0, scale_count: int = 0, work_local_size: int = 0,
                 handle: Optional[IRHandle] = None):
        if handle is not None:
            self.handle = handle
            return
        builder = global_builder.get_ir_builder()
        self.handle = builder.create_asc_ConstructOp(builder.get_asc_AscendQuantConfigType(), [
            _mat(calc_count, KT.int32).to_ir(),
            _mat(offset_count, KT.int32).to_ir(),
            _mat(scale_count, KT.int32).to_ir(),
            _mat(work_local_size, KT.int32).to_ir(),
        ], builder.get_type_array_attr([builder.get_ui32_type()] * 4), isConstexpr=True, isStatic=True)

    @classmethod
    def from_ir(cls, handle: IRHandle) -> QuantConfig:
        return cls(handle=handle)

    def to_ir(self) -> IRHandle:
        return self.handle


class MatmulShapeParams:

    def __init__(self, single_core_m: int = 0, single_core_n: int = 0, single_core_k: int = 0, basic_m: int = 0,
                 basic_n: int = 0, basic_k: int = 0) -> None:
        self.single_core_m = single_core_m
        self.single_core_n = single_core_n
        self.single_core_k = single_core_k
        self.basic_m = basic_m
        self.basic_n = basic_n
        self.basic_k = basic_k


class MatmulQuantParams:

    def __init__(self, is_per_tensor: bool = False, has_anti_quant_offset: bool = False) -> None:
        self.is_per_tensor = is_per_tensor
        self.has_anti_quant_offset = has_anti_quant_offset


class MatmulBatchParams:
    def __init__(self, is_b_batch: bool = False, batch_mode: BatchMode = 1, is_bias_batch: bool = False) -> None:
        self.is_n_batch = is_b_batch
        self.batch_mode = batch_mode
        self.is_bias_batch = is_bias_batch


class MatmulFuncParams:
    def __init__(self, intrinsics_limit: bool = False, en_vec_nd2_nz: bool = False, enable_double_cache: bool = False,
                 enable_l1_cache: bool = False, do_mte2_pre_load: int = 0,
                 iterate_order: IterateOrder = 0, schedule_type: ScheduleType = 0, enable_reuse: bool = True,
                 enable_ub_reuse: bool = False, is_partial_output: bool = False,
                 is_a2_b2_shared: bool = False, is_enable_channel_split: bool = False,
                 enable_kdim_reorder_load: bool = False) -> None:
        self.intrinsics_limit = intrinsics_limit
        self.en_vec_nd2_nz = en_vec_nd2_nz
        self.enable_double_cache = enable_double_cache
        self.enable_l1_cache = enable_l1_cache
        self.do_mte2_pre_load = do_mte2_pre_load
        self.iterate_order = iterate_order
        self.schedule_type = schedule_type
        self.enable_reuse = enable_reuse
        self.enable_ub_reuse = enable_ub_reuse
        self.is_partial_output = is_partial_output
        self.is_a2_b2_shared = is_a2_b2_shared
        self.is_enable_channel_split = is_enable_channel_split
        self.enable_kdim_reorder_load = enable_kdim_reorder_load