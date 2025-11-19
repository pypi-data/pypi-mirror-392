# This program is free software, you can redistribute it and/or modify it.
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# This file is a part of the CANN Open Software.
# Licensed under CANN Open Software License Agreement Version 2.0 (the "License").
# Please refer to the License for details. You may not use this file except in compliance with the License.
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
# See LICENSE in the root of the software repository for the full text of the License.

from enum import IntEnum


class BlockMode(IntEnum):
    BLOCK_MODE_NORMAL = 0,
    BLOCK_MODE_MATRIX = 1,
    BLOCK_MODE_VECTOR = 2,
    BLOCK_MODE_SMALL_CHANNEL = 3,
    BLOCK_MODE_DEPTHWISE = 4,


class CacheMode(IntEnum):
    CACHE_MODE_NORMAL = 0,
    CACHE_MODE_DISABLE = 1,
    CACHE_MODE_LAST = 2,
    CACHE_MODE_PERSISTENT = 4,


class CacheRwMode(IntEnum):
    READ = 1,
    WRITE = 2,
    RW = 3,


class CubeFormat(IntEnum):
    ND = 0
    NZ = 1


class DataFormat(IntEnum):
    ND = 0,
    NZ = 1,
    NCHW = 2,
    NC1HWC0 = 3,
    NHWC = 4,


class DeqScale(IntEnum):
    DEQ_NONE = 0,
    DEQ = 1,
    VDEQ = 2,
    DEQ8 = 3,
    VDEQ8 = 4,
    DEQ16 = 5,
    VDEQ16 = 6,


class HardEvent(IntEnum):
    MTE2_MTE1 = 0
    MTE1_MTE2 = 1
    MTE1_M = 2
    M_MTE1 = 3
    MTE2_V = 4
    V_MTE2 = 5
    MTE3_V = 6
    V_MTE3 = 7
    M_V = 8
    V_M = 9
    V_V = 10
    MTE3_MTE1 = 11
    MTE1_MTE3 = 12
    MTE1_V = 13
    MTE2_M = 14
    M_MTE2 = 15
    V_MTE1 = 16
    M_FIX = 17
    FIX_M = 18
    MTE3_MTE2 = 19
    MTE2_MTE3 = 20
    S_V = 21
    V_S = 22
    S_MTE2 = 23
    MTE2_S = 24
    S_MTE3 = 25
    MTE3_S = 26
    MTE2_FIX = 27
    FIX_MTE2 = 28
    FIX_S = 29
    M_S = 30
    FIX_MTE3 = 31
    MTE1_FIX = 32
    FIX_MTE1 = 33
    FIX_FIX = 34


class PipeID(IntEnum):
    PIPE_S = 0
    PIPE_V = 1
    PIPE_M = 2
    PIPE_MTE1 = 3
    PIPE_MTE2 = 4
    PIPE_MTE3 = 5
    PIPE_ALL = 6
    PIPE_MTE4 = 7
    PIPE_MTE5 = 8
    PIPE_V2 = 9
    PIPE_FIX = 10


class Position(IntEnum):
    GM = 0
    A1 = 1
    A2 = 2
    B1 = 3
    B2 = 4
    C1 = 5
    C2 = 6
    CO1 = 7
    CO2 = 8
    VECIN = 9
    VECOUT = 10
    VECCALC = 11


class pad_t(IntEnum):
    PAD_NONE = 0,
    PAD_MODE1 = 1,
    PAD_MODE2 = 2,
    PAD_MODE3 = 3,
    PAD_MODE4 = 4,
    PAD_MODE5 = 5,
    PAD_MODE6 = 6,
    PAD_MODE7 = 7,
    PAD_MODE8 = 8,


class BatchMode(IntEnum):
    NONE = 0,
    BATCH_LESS_THAN_L1 = 1,
    BATCH_LARGE_THAN_L1 = 2,
    SINGLE_LARGE_THAN_L1 = 3,


class IterateMode(IntEnum):
    ITERATE_MODE_NORMAL = 0b00000001,
    ITERATE_MODE_ALL = 0b00000010,
    ITERATE_MODE_BATCH = 0b00000100,
    ITERATE_MODE_N_BATCH = 0b00001000,
    ITERATE_MODE_DEFAULT = 0b11111111,


class IterateOrder(IntEnum):
    ORDER_M = 0,
    ORDER_N = 1,
    UNDEF = 2,


class ScheduleType(IntEnum):
    INNER_PRODUCT = 0,
    OUTER_PRODUCT = 1,


class LayoutMode(IntEnum):
    NONE = 0,
    NORMAL = 1,
    BSNGD = 2,
    SBNGD = 3,
    BNGS1S2 = 4,


class MatmulConfigMode(IntEnum):
    CONFIG_NORM = 1,
    CONFIG_MDL = 2,
    CONFIG_SPECIALMDL = 3
    CONFIG_IBSHARE = 4