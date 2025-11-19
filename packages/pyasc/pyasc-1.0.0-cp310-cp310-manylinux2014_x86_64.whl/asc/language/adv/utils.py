# This program is free software, you can redistribute it and/or modify it.
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# This file is a part of the CANN Open Software.
# Licensed under CANN Open Software License Agreement Version 2.0 (the "License").
# Please refer to the License for details. You may not use this file except in compliance with the License.
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
# See LICENSE in the root of the software repository for the full text of the License.

from typing import Callable, Optional, TypeVar

T = TypeVar("T", bound=Callable)


def set_quant_scalar_docstring():
    func_introduction = """
    本接口提供对输出矩阵的所有值采用同一系数进行量化或反量化的功能，即整个C矩阵对应一个量化参数，量化参数的shape为[1]。
    """

    cpp_signature = """
    **对应的Ascend C函数原型**

        .. code-block:: c++

            __aicore__ inline void SetQuantScalar(const uint64_t quantScalar)

    """

    param_list = """
    **参数说明**

        - quant_scalar：量化或反量化系数。
    """

    return func_introduction, cpp_signature, param_list, ""


def set_quant_vector_docstring():
    func_introduction = """
    本接口提供对输出矩阵采用向量进行量化或反量化的功能，即对于输入shape为[1, N]的参数向量，
    N值为Matmul矩阵计算时M/N/K中的N值，对输出矩阵的每一列都采用该向量中对应列的系数进行量化或反量化。
    """

    cpp_signature = """
    **对应的Ascend C函数原型**

        .. code-block:: c++

            __aicore__ inline void SetQuantVector(const GlobalTensor<uint64_t>& quantTensor)

    """

    param_list = """
    **参数说明**

        - quant_vector：量化或反量化运算时的参数向量。
    """

    return func_introduction, cpp_signature, param_list, ""


def set_org_shape_docstring():
    func_introduction = """
    设置Matmul计算原始完整的形状M、N、K，单位为元素个数。用于运行时修改shape，比如复用同一个Matmul对象，从不同的矩阵块取数据计算。
    """

    cpp_signature = """
    **对应的Ascend C函数原型**

        .. code-block:: c++

            __aicore__ inline void SetOrgShape(int orgM, int orgN, int orgK)

        .. code-block:: c++
        
            __aicore__ inline void SetOrgShape(int orgM, int orgN, int orgKa, int orgKb, int orgKc = 0)

    """

    param_list = """
    **参数说明**

        - org_m：设置原始完整的形状M大小，单位为元素。
        - org_n：设置原始完整的形状N大小，单位为元素。
        - org_ka：设置矩阵A原始完整的形状Ka大小，单位为元素。
        - org_kb：设置矩阵B原始完整的形状Kb大小，单位为元素。
        - org_kc：设置输出C矩阵的N，单位为元素。需要输入B矩阵的N和输出C矩阵的N不一样时可设置，默认为0（即使用B矩阵的N，不进行修改）。
    备注：Ascend C第一个函数原型对应的python参数：org_m，org_n，org_ka；Ascend C第二个函数原型对应的python参数：org_m，org_n，org_ka，org_kb，org_kc。
    """    

    return func_introduction, cpp_signature, param_list, ""


def set_single_shape_docstring():
    func_introduction = """
    设置Matmul单核计算的形状singleCoreM、singleCoreN、singleCoreK，单位为元素。
    用于运行时修改shape，比如复用Matmul对象来处理尾块。与SetTail接口功能一致，建议使用本接口。
    """

    cpp_signature = """
    **对应的Ascend C函数原型**

        .. code-block:: c++

            __aicore__ inline void SetSingleShape(int singleM, int singleN, int singleK)

    """

    param_list = """
    **参数说明**

        - single_m：设置的singleCoreM大小，单位为元素。
        - single_n：设置的singleCoreN大小，单位为元素。
        - single_k：设置的singleCoreK大小，单位为元素。
    """    

    return func_introduction, cpp_signature, param_list, ""


def set_self_define_data_docstring():
    func_introduction = """
    使能模板参数MatmulCallBackFunc（自定义回调函数）时，设置需要的计算数据或在GM上存储的数据地址等信息，用于回调函数使用。复用同一个Matmul对象时，可以多次调用本接口重新设置对应数据信息。
    """

    cpp_signature = """
    **对应的Ascend C函数原型**

        .. code-block:: c++

            __aicore__ inline void SetSelfDefineData(const uint64_t dataPtr)

        .. code-block:: c++

            __aicore__ inline void SetSelfDefineData(T dataPtr)

    """

    param_list = """
    **参数说明**

        - data_ptr：设置的算子回调函数需要的计算数据或在GM上存储的数据地址等信息。其中，类型T支持用户自定义基础结构体。
    """

    return func_introduction, cpp_signature, param_list, ""


def set_sparse_index_docstring():
    func_introduction = """
    设置稀疏矩阵稠密化过程生成的索引矩阵。
    索引矩阵的Format格式要求为NZ格式。
    本接口仅支持在纯Cube模式（只有矩阵计算）且MDL模板的场景使用。
    """

    cpp_signature = """
    **对应的Ascend C函数原型**

        .. code-block:: c++

            __aicore__ inline void SetSparseIndex(const GlobalTensor<uint8_t>& indexGlobal)
    """

    param_list = """
    **参数说明**

        - index_global：索引矩阵在Global Memory上的首地址，类型为GlobalTensor。
    """

    return func_introduction, cpp_signature, param_list, ""


def set_user_def_info_docstring():
    func_introduction = """
    使能模板参数MatmulCallBackFunc（自定义回调函数）时，设置算子tiling地址，用于回调函数使用，该接口仅需调用一次。
    """

    cpp_signature = """
    **对应的Ascend C函数原型**

        .. code-block:: c++

            __aicore__ inline void SetUserDefInfo(const uint64_t tilingPtr)
    """

    param_list = """
    **参数说明**

        - tiling_ptr：设置的算子tiling地址。
    """

    return func_introduction, cpp_signature, param_list, ""


def get_matmul_api_tiling_docstring():
    func_introduction = """
    本接口用于在编译期间获取常量化的Matmul Tiling参数。
    """

    cpp_signature = """
    **对应的Ascend C函数原型**

        .. code-block:: c++

            template<class A_TYPE, class B_TYPE, class C_TYPE, class BIAS_TYPE>
            __aicore__ constexpr MatmulApiStaticTiling GetMatmulApiTiling(const MatmulConfig& mmCFG, int32_t l1Size = Impl::L1_SIZE)
    """

    param_list = """
    **参数说明**

        - mm_cfg：获取的MatmulConfig模板。
        - l1_size：可用的L1大小，默认值L1_SIZE。
        - a_type：A矩阵类型信息，通过MatmulType来定义。
        - b_type：B矩阵类型信息，通过MatmulType来定义。
        - c_type：C矩阵类型信息，通过MatmulType来定义。
        - bias_type：BIAS矩阵类型信息，通过MatmulType来定义。
    """

    return_list = """
    **返回值说明**
        MatmulApiStaticTiling，常量化Tiling参数。
    """
    return func_introduction, cpp_signature, param_list, return_list


def iterate_n_batch_docstring():
    func_introduction = """
        调用一次IterateNBatch，会进行N次IterateBatch计算，计算出N个多Batch的singleCoreM * singleCoreN大小的C矩阵。
        在调用该接口前，需将MatmulConfig中的isNBatch参数设为true，使能多Batch输入多Batch输出功能，并调用SetWorkspace接口申请临时空间，
        用于缓存计算结果，即IterateNBatch的结果输出至SetWorkspace指定的Global Memory内存中。
        对于BSNGD、SBNGD、BNGS1S2的Layout格式，
        调用该接口之前需要在tiling中使用SetALayout/SetBLayout/SetCLayout/SetBatchNum设置A/B/C的Layout轴信息和最大BatchNum数；
        对于Normal数据格式则需使用SetBatchInfoForNormal设置A/B/C的M/N/K轴信息和A/B矩阵的BatchNum数。
        实例化Matmul时，通过MatmulType设置Layout类型，当前支持3种Layout类型：BSNGD、SBNGD、BNGS1S2。
    """

    cpp_signature = """
    **对应的Ascend C函数原型**

        .. code-block:: c++

            template <bool sync = true, bool waitIterateBatch = false>
            __aicore__ inline void IterateNBatch(const uint32_t batchLoop, uint32_t batchA, uint32_t batchB, bool enSequentialWrite, const uint32_t matrixStrideA = 0, const uint32_t matrixStrideB = 0, const uint32_t matrixStrideC = 0)

    """

    param_list = """
    **参数说明**

        - sync：设置同步或者异步模式。
        - wait_iterate_batch：是否需要通过WaitIterateBatch接口等待IterateNBatch执行结束，仅在异步场景下使用。
        - batch_loop：当前计算的BMM个数。
        - batch_a：当前单次BMM调用计算左矩阵的batch数。
        - batch_b：当前单次BMM调用计算右矩阵的batch数，brc场景batchA/B不相同。
        - en_sequential_write：输出是否连续存放数据。
        - matrix_stride_a：A矩阵源操作数相邻nd矩阵起始地址间的偏移，默认值是0。
        - matrix_stride_b：B矩阵源操作数相邻nd矩阵起始地址间的偏移，默认值是0。
        - matrix_stride_c：该参数预留，开发者无需关注。
    """

    return func_introduction, cpp_signature, param_list, ""


def end_docstring():
    func_introduction = """
        多个Matmul对象之间切换计算时，必须调用一次End函数，用于释放Matmul计算资源，防止多个Matmul对象的计算资源冲突。
    """

    cpp_signature = """
    **对应的Ascend C函数原型**

        .. code-block:: c++

            __aicore__ inline void End()

    """

    param_list = """
    **参数说明**
        无
    """

    return func_introduction, cpp_signature, param_list, ""


def set_hf32_docstring():
    func_introduction = """
        设置是否使能HF32（矩阵乘计算时可采用的数据类型）模式。使能后，在矩阵乘计算时，
        float32数据类型会转换为hf32数据类型，可提升计算性能，但同时也会带来精度损失。
    """

    cpp_signature = """
    **对应的Ascend C函数原型**

        .. code-block:: c++

            __aicore__ inline void SetHF32(bool enableHF32 = false, int32_t transMode = 0)

    """

    param_list = """
    **参数说明**

        - enable_hf32：配置是否开启HF32模式，默认值false(不开启)。
        - trans_mode：配置在开启HF32模式时，float转换为hf32时所采用的ROUND模式。默认值0。
    """

    return func_introduction, cpp_signature, param_list, ""


def set_tail_docstring():
    func_introduction = """
        在不改变Tiling的情况下，重新设置本次计算的singleCoreM/singleCoreN/singleCoreK，以元素为单位。
    """

    cpp_signature = """
    **对应的Ascend C函数原型**

        .. code-block:: c++

            __aicore__ inline void SetTail(int tailM = -1, int tailN = -1, int tailK = -1)

    """

    param_list = """
    **参数说明**

        - tail_m：重新设置的singleCoreM值。
        - tail_n：重新设置的singleCoreN值。
        - tail_k：重新设置的singleCoreK值。
    """

    return func_introduction, cpp_signature, param_list, ""


def set_batch_num_docstring():
    func_introduction = """
        在不改变Tiling的情况下，重新设置多Batch计算的Batch数。
    """

    cpp_signature = """
    **对应的Ascend C函数原型**

        .. code-block:: c++

            __aicore__ inline void SetTail(int tailM = -1, int tailN = -1, int tailK = -1)

    """

    param_list = """
    **参数说明**

        - tail_m：重新设置的singleCoreM值。
        - tail_n：重新设置的singleCoreN值。
        - tail_k：重新设置的singleCoreK值。
    """

    return func_introduction, cpp_signature, param_list, ""


def set_workspace_docstring():
    func_introduction = """
        Iterate计算的异步场景，调用本接口申请一块临时空间来缓存计算结果，然后调用GetTensorC时会在该临时空间中获取C的矩阵分片。
        IterateNBatch计算时，调用本接口申请一块临时空间来缓存计算结果，然后根据同步或异步场景进行其它接口的调用。
    """

    cpp_signature = """
    **对应的Ascend C函数原型**

        .. code-block:: c++

            template <class T> __aicore__ inline void SetWorkspace(GlobalTensor<T>& addr)

        .. code-block:: c++

            template <class T> __aicore__ inline void SetWorkspace(__gm__ const T* addr, int size)

    """

    param_list = """
    **参数说明**

        - addr：用户传入的GM上的workspace空间，GlobalTensor类型。
        - addr：用户传入的GM上的workspace空间，GM地址类型。
        - size：传入GM地址时，需要配合传入元素个数。
    """

    return func_introduction, cpp_signature, param_list, ""


def wait_get_tensor_c_docstring():
    func_introduction = """
        当使用GetTensorC异步接口将结果矩阵从GM拷贝到UB，且UB后续需要进行Vector计算时，需要调用WaitGetTensorC进行同步。
    """

    cpp_signature = """
    **对应的Ascend C函数原型**

        .. code-block:: c++

            __aicore__ inline void WaitGetTensorC()

    """

    param_list = """
    **参数说明**
        无
    """

    return func_introduction, cpp_signature, param_list, ""


def get_offset_c_docstring():
    func_introduction = """
        预留接口，为后续功能做预留。
        获取本次计算时当前分片在整个C矩阵中的位置。
    """

    cpp_signature = """
    **对应的Ascend C函数原型**

        .. code-block:: c++

            __aicore__ inline MatrixOffset GetOffsetC()

    """

    param_list = """
    **参数说明**

        无
    """

    return_list = """
    **MatrixOffset结构体如下：**

        .. code-block:: c++

            struct MatrixOffset {   
                int32_t offset;   
                int32_t row, col;   
                int32_t height, width; 
            };
    """

    return func_introduction, cpp_signature, param_list, return_list


def async_get_tensor_c_docstring():
    func_introduction = """
        获取Iterate接口异步计算的结果矩阵。该接口功能已被GetTensorC覆盖，建议直接使用GetTensorC异步接口。
    """

    cpp_signature = """
    **对应的Ascend C函数原型**

        .. code-block:: c++

            __aicore__ inline void AsyncGetTensorC(const LocalTensor<DstT>& c)

    """

    param_list = """
    **参数说明**

        - c：结果矩阵

    """

    return func_introduction, cpp_signature, param_list, ""


def get_tensor_c_docstring():
    func_introduction = """
    本接口和iterate接口配合使用，用于在调用iterate完成迭代计算后，
    根据MatmulConfig参数中的ScheduleType取值获取一块或两块baseM * baseN大小的矩阵分片。
    """

    cpp_signature = """
    **对应的Ascend C函数原型**

        .. code-block:: c++

            template <bool sync = true>
            __aicore__ inline void GetTensorC(const LocalTensor<DstT>& co2Local, uint8_t enAtomic = 0, bool enSequentialWrite = false)

        .. code-block:: c++

            template <bool sync = true>
            __aicore__ inline void GetTensorC(const GlobalTensor<DstT>& gm, uint8_t enAtomic = 0, bool enSequentialWrite = false)

        .. code-block:: c++

            template <bool sync = true>
            __aicore__ inline void GetTensorC(const GlobalTensor<DstT>& gm, const LocalTensor<DstT>& co2Local, uint8_t enAtomic = 0, bool enSequentialWrite = false)

        .. code-block:: c++

            template <bool sync = true>
            __aicore__ inline GlobalTensor<DstT> GetTensorC(uint8_t enAtomic = 0, bool enSequentialWrite = false)

    """

    param_list = """
    **参数说明**

        - tensor: 取出C矩阵到VECIN/GM。
        - en_atomic: 是否开启Atomic操作，默认值为0。
        - en_sequential_write: 是否开启连续写模式，默认值false。
        - sync: 设置同步或者异步模式。
        - optional_tensor: 取出C矩阵到VECIN，此参数使能时，tensor类型必须为GlobalTensor。
    """

    return func_introduction, cpp_signature, param_list, ""


def iterate_docstring():
    func_introduction = """
    每调用一次Iterate，会计算出一块baseM * baseN的C矩阵。
    """

    cpp_signature = """
    **对应的Ascend C函数原型**

        .. code-block:: c++

            template <bool sync = true>
            __aicore__ inline bool Iterate(bool enPartialSum = false)

        .. code-block:: c++

            template <bool sync = true, typename T>
            __aicore__ inline bool Iterate(bool enPartialSum, const LocalTensor<T>& localCmatrix)

    """

    param_list = """
    **参数说明**

        - en_partial_sum: 是否将矩阵乘的结果累加于现有的CO1数据，默认值为false。
        - sync: 设置同步或者异步模式。
        - local_c_matrix: 由用户申请的CO1上的LocalTensor内存，用于存放矩阵乘的计算结果。
    """

    return func_introduction, cpp_signature, param_list, ""


def iterate_all_docstring():
    func_introduction = """
    调用一次iterate_all，会计算出singleCoreM * singleCoreN大小的C矩阵。
    """

    cpp_signature = """
    **对应的Ascend C函数原型**

        .. code-block:: c++

            template <bool sync = true>
            __aicore__ inline void IterateAll(const GlobalTensor<DstT>& gm, uint8_t enAtomic = 0, bool enSequentialWrite = false, bool waitIterateAll = false, bool fakeMsg = false)

        .. code-block:: c++

            template <bool sync = true>
            __aicore__ inline void IterateAll(const LocalTensor<DstT>& ubCmatrix, uint8_t enAtomic = 0)

    """

    param_list = """
    **参数说明**

        - tensor: C矩阵，类型为GlobalTensor或LocalTensor。
        - en_atomic: 是否开启Atomic操作，默认值为0。
        - sync: 设置同步或者异步模式。
        - en_sequential_write: 是否开启连续写模式，仅支持输出到Global Memory场景。
        - wait_iterate_all: 是否需要通过wait_iterate_all接口等待iterate_all执行结束，仅支持异步输出到Global Memory场景。
        - fake_msg: 仅在IBShare场景和IntraBlockPartSum场景使用，仅在支持输出到Global Memory场景。
    """

    return func_introduction, cpp_signature, param_list, ""


def wait_iterate_all_docstring():
    func_introduction = """
    等待iterate_all异步接口返回，支持连续输出到Global Memory。
    """

    cpp_signature = """
    **对应的Ascend C函数原型**

        .. code-block:: c++

            __aicore__ inline void SetSingleShape(int singleM, int singleN, int singleK)

    """

    param_list = """
    **参数说明**

        无
    """

    return func_introduction, cpp_signature, param_list, ""


def iterate_batch_docstring():
    func_introduction = """
    该接口提供批量处理Matmul的功能，调用一次iterate_batch，可以计算出多个singleCoreM * singleCoreN大小的C矩阵。
    """

    cpp_signature = """
    **对应的Ascend C函数原型**

        .. code-block:: c++

            template <bool sync = true, bool waitIterateBatch = false>
            __aicore__ inline void IterateBatch(const GlobalTensor<DstT>& gm, uint32_t batchA, uint32_t batchB, bool enSequentialWrite, const uint32_t matrixStrideA = 0, const uint32_t matrixStrideB = 0, const uint32_t matrixStrideC = 0, const bool enPartialSum = false, const uint8_t enAtomic = 0)

        .. code-block:: c++

            template <bool sync = true>
            __aicore__ inline void IterateBatch(const LocalTensor<DstT>& ubCmatrix, uint32_t batchA, uint32_t batchB, bool enSequentialWrite, const uint32_t matrixStrideA = 0, const uint32_t matrixStrideB = 0, const uint32_t matrixStrideC = 0, const bool enPartialSum = false, const uint8_t enAtomic = 0)

        .. code-block:: c++

            __aicore__ inline void IterateBatch(const GlobalTensor<DstT>& gm, bool enPartialSum, uint8_t enAtomic, bool enSequentialWrite, const uint32_t matrixStrideA = 0, const uint32_t matrixStrideB = 0, const uint32_t matrixStrideC = 0)

        .. code-block:: c++

            __aicore__ inline void IterateBatch(const LocalTensor<DstT>& ubCmatrix, bool enPartialSum, uint8_t enAtomic, bool enSequentialWrite, const uint32_t matrixStrideA = 0, const uint32_t matrixStrideB = 0, const uint32_t matrixStrideC = 0)

    """

    param_list = """
    **参数说明**

        - tensor: C矩阵。类型为GlobalTensor或LocalTensor。
        - batch_a: 左矩阵的batch数。
        - batch_b: 右矩阵的batch数。
        - en_sequential_write: 是否开启连续写模式。
        - matrix_stride_a: A矩阵源操作数相邻nd矩阵起始地址间的偏移，单位是元素，默认值是0。
        - matrix_stride_b: B矩阵源操作数相邻nd矩阵起始地址间的偏移，单位是元素，默认值是0。
        - matrix_stride_c: 该参数预留，开发者无需关注。
        - en_partial_sum: 是否将矩阵乘的结果累加于现有的CO1数据，默认值为false。
        - en_atomic: 是否开启Atomic操作，默认值为0。
        - sync: 设置同步或者异步模式。
        - wait_iterate_batch: 是否需要通过wait_iterate_batch接口等待iterate_batch执行结束，仅在异步场景下使用。
    """

    return func_introduction, cpp_signature, param_list, ""


def wait_iterate_batch_docstring():
    func_introduction = """
    等待iterate_batch异步接口或iterate_nbatch异步接口返回，支持连续输出到Global Memory。
    """

    cpp_signature = """
    **对应的Ascend C函数原型**

        .. code-block:: c++

            __aicore__ inline void WaitIterateBatch()

    """

    param_list = """
    **参数说明**

        无
    """

    return func_introduction, cpp_signature, param_list, ""


def get_batch_tensor_c_docstring():
    func_introduction = """
    调用一次get_batch_tensor_c，会获取C矩阵片，该接口可以与iterate_n_batch异步接口配合使用。
    用于在调用iterate_n_batch迭代计算后，获取一片std::max(batch_a, batch_b) * singleCoreM * singleCoreN大小的矩阵分片。
    """

    cpp_signature = """
    **对应的Ascend C函数原型**

        .. code-block:: c++

            template <bool sync = true>
            __aicore__ inline GlobalTensor<DstT> GetBatchTensorC(uint32_t batchA, uint32_t batchB, bool enSequentialWrite = false)

        .. code-block:: c++

            template <bool sync = true>
            __aicore__ inline void GetBatchTensorC(const LocalTensor<DstT>& c, uint32_t batchA, uint32_t batchB, bool enSequentialWrite = false)

    """

    param_list = """
    **参数说明**

        - batch_a: 左矩阵的batch数。
        - batch_b: 右矩阵的batch数。
        - en_sequential_write: 该参数预留，开发者无需关注。
        - tensor: C矩阵放置于Local Memory的地址，用于保存矩阵分片。
    """

    return func_introduction, cpp_signature, param_list, ""


def set_tensor_a_docstring():
    func_introduction = """
    设置矩阵乘的左矩阵A。
    """

    cpp_signature = """
    **对应的Ascend C函数原型**

        .. code-block:: c++

            __aicore__ inline void SetTensorA(const GlobalTensor<SrcAT>& gm, bool isTransposeA = false)

        .. code-block:: c++

            __aicore__ inline void SetTensorA(const LocalTensor<SrcAT>& leftMatrix, bool isTransposeA = false)

        .. code-block:: c++

            __aicore__ inline void SetTensorA(SrcAT aScalar)

    """

    param_list = """
    **参数说明**

        - scalar: A矩阵中设置的值，为标量。
        - tensor: A矩阵。类型为GlobalTensor或LocalTensor。
        - transpose: A矩阵是否需要转置。
    """

    return func_introduction, cpp_signature, param_list, ""


def set_tensor_b_docstring():
    func_introduction = """
    设置矩阵乘的右矩阵B。
    """

    cpp_signature = """
    **对应的Ascend C函数原型**

        .. code-block:: c++

            __aicore__ inline void SetTensorB(const GlobalTensor<SrcBT>& gm, bool isTransposeB = false)

        .. code-block:: c++

            __aicore__ inline void SetTensorB(const LocalTensor<SrcBT>& leftMatrix, bool isTransposeB = false)

        .. code-block:: c++

            __aicore__ inline void SetTensorB(SrcBT bScalar)

    """

    param_list = """
    **参数说明**

        - scalar: B矩阵中设置的值，为标量。
        - tensor: B矩阵。类型为GlobalTensor或LocalTensor。
        - transpose: B矩阵是否需要转置。
    """

    return func_introduction, cpp_signature, param_list, ""


def set_bias_docstring():
    func_introduction = """
    设置矩阵乘的Bias。
    """

    cpp_signature = """
    **对应的Ascend C函数原型**

        .. code-block:: c++

            __aicore__ inline void SetBias(const GlobalTensor<BiasT>& biasGlobal)

        .. code-block:: c++

            __aicore__ inline void SetBias(const LocalTensor<BiasT>& inputBias)

    """

    param_list = """
    **参数说明**

        - tensor: Bias矩阵。类型为GlobalTensor或LocalTensor。
    """

    return func_introduction, cpp_signature, param_list, ""


def disable_bias_docstring():
    func_introduction = """
    清除Bias标志位，表示Matmul计算时没有Bias参与。
    """

    cpp_signature = """
    **对应的Ascend C函数原型**

        .. code-block:: c++

            __aicore__ inline void DisableBias()

    """

    param_list = """
    **参数说明**

        无
    """

    return func_introduction, cpp_signature, param_list, ""


def set_matmul_docstring(api_name: Optional[str] = None) -> Callable[[T], T]:
    func_introduction = ""
    cpp_signature = ""
    param_list = ""
    return_list = ""
    if api_name == "set_quant_scalar":
        func_introduction, cpp_signature, param_list, return_list = set_quant_scalar_docstring()
    elif api_name == "set_quant_vector":
        func_introduction, cpp_signature, param_list, return_list = set_quant_vector_docstring()
    elif api_name == "set_org_shape":
        func_introduction, cpp_signature, param_list, return_list = set_org_shape_docstring()
    elif api_name == "set_single_shape":
        func_introduction, cpp_signature, param_list, return_list = set_single_shape_docstring()
    elif api_name == "set_self_define_data":
        func_introduction, cpp_signature, param_list, return_list = set_self_define_data_docstring()
    elif api_name == "set_user_def_info":
        func_introduction, cpp_signature, param_list, return_list = set_user_def_info_docstring()
    elif api_name == "set_sparse_index":
        func_introduction, cpp_signature, param_list, return_list = set_sparse_index_docstring()
    elif api_name == "get_matmul_api_tiling":
        func_introduction, cpp_signature, param_list, return_list = get_matmul_api_tiling_docstring()
    elif api_name == "iterate_n_batch":
        func_introduction, cpp_signature, param_list, return_list = iterate_n_batch_docstring()
    elif api_name == "end":
        func_introduction, cpp_signature, param_list, return_list = end_docstring()
    elif api_name == "set_hf32":
        func_introduction, cpp_signature, param_list, return_list = set_hf32_docstring()
    elif api_name == "set_tail":
        func_introduction, cpp_signature, param_list, return_list = set_tail_docstring()
    elif api_name == "set_batch_num":
        func_introduction, cpp_signature, param_list, return_list = set_batch_num_docstring()
    elif api_name == "set_workspace":
        func_introduction, cpp_signature, param_list, return_list = set_workspace_docstring()
    elif api_name == "wait_get_tensor_c":
        func_introduction, cpp_signature, param_list, return_list = wait_get_tensor_c_docstring()
    elif api_name == "get_offset_c":
        func_introduction, cpp_signature, param_list, return_list = get_offset_c_docstring()
    elif api_name == "async_get_tensor_c":
        func_introduction, cpp_signature, param_list, return_list = async_get_tensor_c_docstring()
    elif api_name == "set_tensor_a":
        func_introduction, cpp_signature, param_list, return_list = set_tensor_a_docstring()
    elif api_name == "set_tensor_b":
        func_introduction, cpp_signature, param_list, return_list = set_tensor_b_docstring()
    elif api_name == "set_bias":
        func_introduction, cpp_signature, param_list, return_list = set_bias_docstring()
    elif api_name == "disable_bias":
        func_introduction, cpp_signature, param_list, return_list = disable_bias_docstring()
    elif api_name == "get_batch_tensor_c":
        func_introduction, cpp_signature, param_list, return_list = get_batch_tensor_c_docstring()
    elif api_name == "iterate":
        func_introduction, cpp_signature, param_list, return_list = iterate_docstring()
    elif api_name == "get_tensor_c":
        func_introduction, cpp_signature, param_list, return_list = get_tensor_c_docstring()
    elif api_name == "iterate_all":
        func_introduction, cpp_signature, param_list, return_list = iterate_all_docstring()
    elif api_name == "wait_iterate_all":
        func_introduction, cpp_signature, param_list, return_list = wait_iterate_all_docstring()
    elif api_name == "iterate_batch":
        func_introduction, cpp_signature, param_list, return_list = iterate_batch_docstring()
    elif api_name == "wait_iterate_batch":
        func_introduction, cpp_signature, param_list, return_list = wait_iterate_batch_docstring()
    else:
        raise RuntimeError(f"Invalid matmul api name {api_name}")

    docstr = f"""
    {func_introduction}
    {cpp_signature}
    {param_list}
    {return_list}
    """

    def decorator(fn: T) -> T:
        fn.__doc__ = docstr
        return fn

    return decorator
