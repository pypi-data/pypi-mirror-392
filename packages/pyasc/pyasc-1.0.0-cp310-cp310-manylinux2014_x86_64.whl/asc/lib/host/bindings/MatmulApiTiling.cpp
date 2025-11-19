/*
 * This program is free software, you can redistribute it and/or modify it.
 * Copyright (c) 2025 Huawei Technologies Co., Ltd.
 * This file is a part of the CANN Open Software.
 * Licensed under CANN Open Software License Agreement Version 2.0 (the "License").
 * Please refer to the License for details. You may not use this file except in compliance with the License.
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
 * INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
 * See LICENSE in the root of the software repository for the full text of the License.
 */

#include <cstdint>
#include "kernel_tiling/kernel_tiling.h"
#include "tiling/platform/platform_ascendc.h"
#include "tiling/tiling_api.h"

#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace pybind11 {
namespace asc {
void pyasc_init_matmul_api_tiling(py::module &m) {
  using namespace matmul_tiling;

  // MatmulConfigParams struct
  py::class_<MatmulConfigParams>(m, "MatmulConfigParams", py::module_local())
      .def(py::init<int32_t, bool, ScheduleType, MatrixTraverse, bool>(),
                    "mm_config_type"_a = 1, "enable_l1_cache_ub"_a = false,
                    "schedule_type"_a = ScheduleType::INNER_PRODUCT,
                    "traverse"_a = MatrixTraverse::NOSET, "en_vec_nd2nz"_a = false)
           .def_readwrite("mm_config_type", &MatmulConfigParams::mmConfigType)
           .def_readwrite("enable_l1_cache_ub", &MatmulConfigParams::enableL1CacheUB)
           .def_readwrite("schedule_type", &MatmulConfigParams::scheduleType)
           .def_readwrite("traverse", &MatmulConfigParams::traverse)
           .def_readwrite("en_vec_nd2nz", &MatmulConfigParams::enVecND2NZ);

  // MatmulApiTilingBase class
  py::class_<MatmulApiTilingBase>(m, "MatmulApiTilingBase", py::module_local())
      // Set methods
      .def("set_a_type", [](MatmulApiTilingBase &self, TPosition pos, CubeFormat type, DataType dataType,
                            bool isTrans) { return self.SetAType(pos, type, dataType, isTrans); },
                            "pos"_a, "type"_a, "data_type"_a, "is_trans"_a)
      .def("set_b_type", [](MatmulApiTilingBase &self, TPosition pos, CubeFormat type, DataType dataType,
                            bool isTrans) { return self.SetBType(pos, type, dataType, isTrans); },
                            "pos"_a, "type"_a, "data_type"_a, "is_trans"_a)
      .def("set_c_type", [](MatmulApiTilingBase &self, TPosition pos, CubeFormat type,
                            DataType dataType) { return self.SetCType(pos, type, dataType); },
                            "pos"_a, "type"_a, "data_type"_a)
      .def("set_bias_type", [](MatmulApiTilingBase &self, TPosition pos, CubeFormat type,
                               DataType dataType) { return self.SetBiasType(pos, type, dataType); },
                               "pos"_a, "type"_a, "data_type"_a)
      .def("set_shape",
           [](MatmulApiTilingBase &self, int32_t m, int32_t n, int32_t k) { return self.SetShape(m, n, k); },
           "m"_a, "n"_a, "k"_a)
      .def("set_org_shape", [](MatmulApiTilingBase &self, int32_t orgMIn, int32_t orgNIn,
                               int32_t orgKIn) { return self.SetOrgShape(orgMIn, orgNIn, orgKIn); },
                               "org_m_in"_a, "org_n_in"_a, "org_k_in"_a)
      .def("set_org_shape", [](MatmulApiTilingBase &self, int32_t orgMIn, int32_t orgNIn, int32_t orgKaIn,
                               int32_t orgKbIn) { return self.SetOrgShape(orgMIn, orgNIn, orgKaIn, orgKbIn); },
                               "org_m_in"_a, "org_n_in"_a, "org_ka_in"_a, "org_kb_in"_a)
      .def(
          "set_fix_split",
          [](MatmulApiTilingBase &self, int32_t baseMIn, int32_t baseNIn, int32_t baseKIn) {
            return self.SetFixSplit(baseMIn, baseNIn, baseKIn);
          },
          "base_m_in"_a = -1, "base_n_in"_a = -1, "base_k_in"_a = -1)
      .def(
          "set_buffer_space",
          [](MatmulApiTilingBase &self, int32_t l1Size, int32_t l0CSize, int32_t ubSize, int32_t btSize) {
            return self.SetBufferSpace(l1Size, l0CSize, ubSize, btSize);
          },
          "l1_size"_a = -1, "l0_c_size"_a = -1, "ub_size"_a = -1, "bt_size"_a = -1)
      .def("set_traverse",
           [](MatmulApiTilingBase &self, MatrixTraverse traverse) { return self.SetTraverse(traverse); },
           "traverse"_a)
      .def("set_mad_type", [](MatmulApiTilingBase &self, MatrixMadType madType) { return self.SetMadType(madType); },
           "mad_type"_a)
      .def(
          "set_split_range",
          [](MatmulApiTilingBase &self, int32_t maxBaseM, int32_t maxBaseN, int32_t maxBaseK, int32_t minBaseM,
             int32_t minBaseN, int32_t minBaseK) {
            return self.SetSplitRange(maxBaseM, maxBaseN, maxBaseK, minBaseM, minBaseN, minBaseK);
          },
          "max_base_m"_a = -1, "max_base_n"_a = -1, "max_base_k"_a = -1, "min_base_m"_a = -1, "min_base_n"_a = -1,
          "min_base_k"_a = -1)
      .def(
          "set_double_buffer",
          [](MatmulApiTilingBase &self, bool a, bool b, bool c, bool bias, bool transND2NZ, bool transNZ2ND) {
            return self.SetDoubleBuffer(a, b, c, bias, transND2NZ, transNZ2ND);
          },
          "a"_a, "b"_a, "c"_a, "bias"_a, "trans_nd2nz"_a = true, "trans_nz2nd"_a = true)
      .def("set_dequant_type",
           [](MatmulApiTilingBase &self, DequantType dequantType) { return self.SetDequantType(dequantType); },
           "dequant_type"_a)
      .def("set_a_layout", [](MatmulApiTilingBase &self, int32_t b, int32_t s, int32_t n, int32_t g,
                              int32_t d) { return self.SetALayout(b, s, n, g, d); },
                              "b"_a, "s"_a, "n"_a, "g"_a, "d"_a)
      .def("set_b_layout", [](MatmulApiTilingBase &self, int32_t b, int32_t s, int32_t n, int32_t g,
                              int32_t d) { return self.SetBLayout(b, s, n, g, d); },
                              "b"_a, "s"_a, "n"_a, "g"_a, "d"_a)
      .def("set_c_layout", [](MatmulApiTilingBase &self, int32_t b, int32_t s, int32_t n, int32_t g,
                              int32_t d) { return self.SetCLayout(b, s, n, g, d); },
                              "b"_a, "s"_a, "n"_a, "g"_a, "d"_a)
      .def("set_batch_num", [](MatmulApiTilingBase &self, int32_t batch) { return self.SetBatchNum(batch); },
           "batch"_a)
      .def("set_batch_info_for_normal",
           [](MatmulApiTilingBase &self, int32_t batchA, int32_t batchB, int32_t m, int32_t n, int32_t k) {
             return self.SetBatchInfoForNormal(batchA, batchB, m, n, k);
           }, "batch_a"_a, "batch_b"_a, "m"_a, "n"_a, "k"_a)
      .def(
          "set_matmul_config_params",
          [](MatmulApiTilingBase &self, int32_t mmConfigType, bool enableL1CacheUB, ScheduleType scheduleType,
             MatrixTraverse traverse, bool enVecND2NZ) {
            return self.SetMatmulConfigParams(mmConfigType, enableL1CacheUB, scheduleType, traverse,
                                              enVecND2NZ);
          },
          "mm_config_type"_a = 1, "enable_l1_cache_ub"_a = false, "schedule_type"_a = ScheduleType::INNER_PRODUCT,
          "traverse"_a = MatrixTraverse::NOSET, "en_vec_nd2nz"_a = false)
      .def("set_matmul_config_params",
           [](MatmulApiTilingBase &self, const MatmulConfigParams &configParams) {
             return self.SetMatmulConfigParams(configParams);
           }, "config_params"_a)
      .def(
          "set_bias", [](MatmulApiTilingBase &self, bool isBiasIn) { return self.SetBias(isBiasIn); },
          "is_bias_in"_a = false)
      .def(
          "set_sparse", [](MatmulApiTilingBase &self, bool isSparceIn) { return self.SetSparse(isSparceIn); },
          "is_sparce_in"_a = false)
      // Get methods
      .def("get_base_m", [](MatmulApiTilingBase &self) { return self.GetBaseM(); })
      .def("get_base_n", [](MatmulApiTilingBase &self) { return self.GetBaseN(); })
      .def("get_base_k", [](MatmulApiTilingBase &self) { return self.GetBaseK(); })
      .def("get_tiling",
           [](MatmulApiTilingBase &self, py::object &tiling) {
             py::object method = tiling.attr("addressof");
             py::object result = method();
             auto cpp_int = py::cast<size_t>(result);
             auto *tiling_new = reinterpret_cast<TCubeTiling *>(cpp_int);
             return self.GetTiling(*tiling_new);
           }, "tiling"_a)
      // Enable methods
      .def(
          "enable_bias", [](MatmulApiTilingBase &self, bool isBiasIn) { return self.EnableBias(isBiasIn); },
          "is_bias_in"_a = false);

  // MatmulApiTiling class
  py::class_<MatmulApiTiling, MatmulApiTilingBase>(m, "MatmulApiTiling", py::module_local())
      .def(py::init<const platform_ascendc::PlatformAscendC &>());

  // MultiCoreMatmulTiling class
  py::class_<MultiCoreMatmulTiling, MatmulApiTilingBase>(m, "MultiCoreMatmulTiling", py::module_local())
      .def(py::init<const platform_ascendc::PlatformAscendC &>())
      // Set methods
      .def("set_dim", [](MultiCoreMatmulTiling &self, int32_t dim) { return self.SetDim(dim); },
           "dim"_a)
      .def("set_shape",
           [](MultiCoreMatmulTiling &self, int32_t m, int32_t n, int32_t k) { return self.SetShape(m, n, k); },
           "m"_a, "n"_a, "k"_a)
      .def(
          "set_single_shape",
          [](MultiCoreMatmulTiling &self, int32_t singleMIn, int32_t singleNIn, int32_t singleKIn) {
            return self.SetSingleShape(singleMIn, singleNIn, singleKIn);
          },
          "single_m_in"_a = -1, "single_n_in"_a = -1, "single_k_in"_a = -1)
      .def(
          "set_single_range",
          [](MultiCoreMatmulTiling &self, int32_t maxM, int32_t maxN, int32_t maxK, int32_t minM, int32_t minN,
             int32_t minK) { return self.SetSingleRange(maxM, maxN, maxK, minM, minN, minK); },
          "max_m"_a = -1, "max_n"_a = -1, "max_k"_a = -1, "min_m"_a = -1, "min_n"_a = -1, "min_k"_a = -1)
      .def("set_align_split", [](MultiCoreMatmulTiling &self, int32_t alignM, int32_t alignN,
                                 int32_t alignK) { return self.SetAlignSplit(alignM, alignN, alignK); },
                                 "align_m"_a, "align_n"_a, "align_k"_a)
      .def("set_split_k", [](MultiCoreMatmulTiling &self, bool flag) { return self.SetSplitK(flag); },
           "flag"_a)
      // Get methods
      .def("get_single_shape", [](MultiCoreMatmulTiling &self) -> py::object {
                                    int32_t shapeM, shapeN, shapeK;
                                    auto ret = self.GetSingleShape(shapeM, shapeN, shapeK);
                                    if (ret != 0) {
                                      return py::none();
                                    } else {
                                      return py::make_tuple(shapeM, shapeN, shapeK);
                                    }
                                  })
      .def("get_core_num", [](MultiCoreMatmulTiling &self) -> py::object {
                                int32_t dim, mDim, nDim;
                                auto ret = self.GetCoreNum(dim, mDim, nDim);
                                if (ret != 0) {
                                  return py::none();
                                } else {
                                  return py::make_tuple(dim, mDim, nDim);
                                }
                              })
      // Enable methods
      .def("enable_multi_core_split_k",
           [](MultiCoreMatmulTiling &self, bool flag) { return self.EnableMultiCoreSplitK(flag); },
           "flag"_a);

  // BatchMatmulTiling class
  py::class_<BatchMatmulTiling, MatmulApiTilingBase>(m, "BatchMatmulTiling", py::module_local())
      .def(py::init<const platform_ascendc::PlatformAscendC &>())
      // Get methods
      .def("get_core_num",
           [](BatchMatmulTiling &self) -> py::object {
                int32_t dim, mDim, nDim, batchCoreM, batchCoreN;
                auto ret = self.GetCoreNum(dim, mDim, nDim, batchCoreM, batchCoreN);
                if (ret != 0) {
                  return py::none();
                } else {
                  return py::make_tuple(dim, mDim, nDim, batchCoreM, batchCoreN);
                }
              });
}
} // namespace asc
} // namespace pybind11
