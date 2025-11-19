# This program is free software, you can redistribute it and/or modify it.
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# This file is a part of the CANN Open Software.
# Licensed under CANN Open Software License Agreement Version 2.0 (the "License").
# Please refer to the License for details. You may not use this file except in compliance with the License.
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
# See LICENSE in the root of the software repository for the full text of the License.

from dataclasses import dataclass
import functools
import inspect
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, TypeVar, Union, get_args, get_origin
from typing_extensions import ParamSpec, TypeAlias

from ..._C import ir
from ...common.compat import isinstance
from .constexpr import ConstExpr

FnT = TypeVar("FnT", bound=Callable)
T = TypeVar("T")
P = ParamSpec("P")

JIT_INTERNAL = "__jit__"


@dataclass
class DefaultValued:
    arg_type: Type
    default: Optional[Any]


OverloadArg: TypeAlias = Union[Type, DefaultValued]


@dataclass
class Overload:
    args: Dict[str, OverloadArg]
    impl: Callable


class OverloadDispatcher:

    def __init__(self, name: str = "<overloaded-function>"):
        self.name = name
        self.overloads: List[Overload] = []

    def __call__(self, /, *args, **kwargs) -> Optional[Any]:
        for overload in self.overloads:
            call_args = self.match_overload(overload.args, args, kwargs)
            if call_args is None:
                continue
            return overload.impl(**call_args)
        candidates = []
        sig_str_args = ", ".join(get_type_name(type(value)) for value in args)
        sig_str_kwargs = ", ".join(f"{name}: {get_type_name(type(value))}" for name, value in kwargs.items())
        sig_str = ", ".join([sig_str_args, sig_str_kwargs])
        for idx, overload in enumerate(self.overloads, start=1):
            chunks = []
            for name, arg in overload.args.items():
                if isinstance(arg, DefaultValued):
                    chunks.append(f"{name}: {get_type_name(arg.arg_type)} = {arg.default!r}")
                else:
                    chunks.append(f"{name}: {get_type_name(arg)}")
            arg_str = ", ".join(chunks)
            candidates.append(f"  {idx}. def {self.name}(..., {arg_str}) -> Optional[Any]: ...")
        candidates_str = "\n".join(candidates)
        raise RuntimeError(f"No viable candidates were found to dispatch {self.name}()\n"
                           f"Provided arguments:\n  (..., {sig_str})\n"
                           f"Registered candidates:\n{candidates_str}")

    @staticmethod
    def check_type(value: Optional[Any], arg: OverloadArg) -> bool:
        arg_type = arg
        if isinstance(arg, DefaultValued):
            arg_type = arg.arg_type
        return isinstance(value, arg_type)

    @classmethod
    def match_overload(cls, overload: Dict[str, OverloadArg], args: Tuple[Any],
                       kwargs: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        call_args = {}
        unmatched_args = set(overload)
        if args:
            arg_names = tuple(overload.keys())
            pos_args = arg_names[:len(args)]
            if len(pos_args) != len(args):
                return None
            for name, value in zip(pos_args, args):
                if not cls.check_type(value, overload[name]):
                    return None
                call_args[name] = value
                unmatched_args.discard(name)
        for name, value in kwargs.items():
            if name not in unmatched_args:
                return None
            if not cls.check_type(value, overload[name]):
                return None
            call_args[name] = value
            unmatched_args.discard(name)
        for name in unmatched_args:
            arg = overload[name]
            if not isinstance(arg, DefaultValued):
                return None
            call_args[name] = arg.default
        return call_args

    def add_overload(self, overload: Overload) -> None:
        if len(overload.args) == 0:
            raise ValueError("Overload must have at least one argument")
        if not callable(overload.impl):
            raise ValueError("Overload impl must be callable")
        self.overloads.append(overload)

    def register(self, **kwargs: OverloadArg) -> Callable[[FnT], FnT]:

        def decorator(fn: FnT) -> FnT:
            self.add_overload(Overload(kwargs, fn))
            return fn

        return decorator

    def register_auto(self, fn: FnT, /) -> FnT:
        signature = inspect.signature(fn)
        overload_args = {}
        for name, param in signature.parameters.items():
            cur_arg_type = param.annotation
            if cur_arg_type is inspect._empty:
                raise ValueError(f"Parameter {name} of {fn.__name__} function does not have a type annotation")
            if param.default is not inspect._empty:
                cur_arg_type = DefaultValued(cur_arg_type, param.default)
            overload_args[name] = cur_arg_type
        self.add_overload(Overload(overload_args, fn))
        return fn


class GlobalBuilder:

    def __init__(self):
        self.builder: Optional[ir.Builder] = None
        self.ir_module: Optional[ir.ModuleOp] = None
        self.teardown_callbacks: List[Callable[[], None]] = []

    def set_ir_builder(self, context: ir.Context) -> None:
        self.builder = ir.Builder(context)
        self.ir_module = self.builder.create_ModuleOp()
        self.builder.set_insertion_point_to_start(self.ir_module.get_body())

        def reset():
            self.builder = None

        self.on_teardown(reset)

    def get_ir_builder(self) -> ir.Builder:
        return self.builder

    def get_ir_module(self) -> ir.ModuleOp:
        return self.ir_module

    def on_teardown(self, callback: Callable[[], None]) -> None:
        if not callable(callback):
            raise TypeError("GlobalBuilder teardown callback must be callable")
        self.teardown_callbacks.append(callback)

    def teardown(self) -> None:
        for callback in reversed(self.teardown_callbacks):
            callback()
        self.teardown_callbacks.clear()


global_builder = GlobalBuilder()


def ceildiv(x: int, y: int) -> int:
    return (x + y - 1) // y


def get_type_name(t: Type) -> str:
    origin = get_origin(t)
    if origin:
        if origin is Union:
            types = ", ".join(get_type_name(t) for t in get_args(t))
            return f"Union[{types}]"
        return str(t)
    name = getattr(t, "__name__", None)
    if name:
        return name
    return repr(t)


def check_type(name: str, value: Any, constraint: Type) -> None:
    if isinstance(value, constraint):
        return
    raise TypeError(f"'{name}' argument must be {get_type_name(constraint)}, got {value.__class__.__name__}")


def require_jit(fn: Callable[P, T]) -> Callable[P, T]:
    if not callable(fn):
        raise TypeError(f"{fn} must be a callable function to require jit")

    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        if not isinstance(global_builder.get_ir_builder(), ir.Builder):
            caller_name = fn.__qualname__
            raise RuntimeError(f"'{caller_name}' cannot be called without initialization of global builder")
        return fn(*args, **kwargs)

    return wrapper


def static_assert(test: bool, message: Optional[str] = None) -> None:
    test = ConstExpr.unwrap(test)
    if not isinstance(test, bool):
        raise TypeError(f"Assertion condition could not be determined, expected bool, got {test.__class__.__name__}")
    if not test:
        if message is not None:
            raise AssertionError(message)
        else:
            raise ValueError("miss message")


class GlobalTensorDocstring:

    def __init__(self) -> None:
        ...
    
    @staticmethod
    def set_global_buffer_docstring():
        func_introduction = """
        传入全局数据地址，初始化GlobalTensor。
        """

        cpp_signature = """
        **对应的Ascend C函数原型**

            .. code-block:: c++

                __aicore__ inline void SetGlobalBuffer(__gm__ PrimType* buffer, uint64_t bufferSize)

            .. code-block:: c++

                __aicore__ inline void SetGlobalBuffer(__gm__ PrimType* buffer)

        """

        param_list = """
        **参数说明**

            - buffer：Host侧传入的全局数据指针。PrimType类型。
            - buffer_size：	GlobalTensor所包含的类型为PrimType的数据个数，需自行保证不会超出实际数据的长度。
        """

        return func_introduction, cpp_signature, param_list, ""
    
    @staticmethod
    def get_phy_addr_docstring():
        func_introduction = """
        获取全局数据的地址。
        """

        cpp_signature = """
        **对应的Ascend C函数原型**

            .. code-block:: c++

                __aicore__ inline const __gm__ PrimType* GetPhyAddr() const
            
            .. code-block:: c++

                __aicore__ inline __gm__ PrimType* GetPhyAddr(const uint64_t offset) const

        """

        param_list = """
        **参数说明**

            - offset：偏移的元素个数，用于指定数据的位置。
        """

        return_list = """
        **返回值说明**

            全局数据的地址。
        """

        return func_introduction, cpp_signature, param_list, return_list

    @staticmethod
    def get_value_docstring():
        func_introduction = """
        获取GlobalTensor的相应偏移位置的值。
        """

        cpp_signature = """
        **对应的Ascend C函数原型**

            .. code-block:: c++

                __aicore__ inline __inout_pipe__(S) PrimType GetValue(const uint64_t offset) const

        """

        param_list = """
        **参数说明**

            - offset：偏移offset个元素。
        """

        return_list = """
        **返回值说明**

            返回PrimType类型的立即数。
        """

        return func_introduction, cpp_signature, param_list, return_list

    @staticmethod
    def set_value_docstring():
        func_introduction = """
        设置GlobalTensor相应偏移位置的值。
        """

        cpp_signature = """
        **对应的Ascend C函数原型**

            .. code-block:: c++

                __aicore__ inline void SetValue(const uint64_t offset, PrimType value)

        """

        param_list = """
        **参数说明**

            - offset：偏移offset个元素。
            - value：设置值。PrimType类型。
        """

        return func_introduction, cpp_signature, param_list, ""

    @staticmethod
    def get_size_docstring():
        func_introduction = """
        获取GlobalTensor的元素个数。
        """

        cpp_signature = """
        **对应的Ascend C函数原型**

            .. code-block:: c++

                __aicore__ inline uint64_t GetSize() const

        """

        param_list = """
        **参数说明**

            无。
        """

        return_list = """
        **返回值说明**

            GlobalTensor的元素个数。
        """

        return func_introduction, cpp_signature, param_list, return_list

    @staticmethod
    def set_shape_info_docstring():
        func_introduction = """
        设置GlobalTensor的shape信息。
        """

        cpp_signature = """
        **对应的Ascend C函数原型**

            .. code-block:: c++

                __aicore__ inline void SetShapeInfo(const ShapeInfo& shapeInfo)

        """

        param_list = """
        **参数说明**

            - shape_info：ShapeInfo结构体。
        """

        return func_introduction, cpp_signature, param_list, ""
    
    @staticmethod
    def get_shape_info_docstring():
        func_introduction = """
        获取GlobalTensor的shape信息。注意：Shape信息没有默认值，只有通过SetShapeInfo设置过Shape信息后，才可以调用该接口获取正确的ShapeInfo。
        """

        cpp_signature = """
        **对应的Ascend C函数原型**

            .. code-block:: c++

                __aicore__ inline ShapeInfo GetShapeInfo() const

        """

        param_list = """
        **参数说明**

            无。
        """

        return_list = """
        **返回值说明**

            GlobalTensor的shape信息，ShapeInfo类型。
        """
        
        return func_introduction, cpp_signature, param_list, return_list
    
    @staticmethod
    def set_l2_cache_hint_docstring():
        func_introduction = """
        设置GlobalTensor是否使能L2 Cache，默认使能L2 Cache。
        """

        cpp_signature = """
        **对应的Ascend C函数原型**

            .. code-block:: c++

                template<CacheRwMode rwMode = CacheRwMode::RW>
                __aicore__ inline void SetL2CacheHint(CacheMode mode);

        """

        param_list = """
        **参数说明**

            - rw_mode：设置L2 Cache读写模式。
            - mode：用户指定的L2 Cache模式。
        """
        
        return func_introduction, cpp_signature, param_list, ""


class LocalTensorDocstring:

    def __init__(self) -> None:
        ...
    
    @staticmethod
    def set_value_docstring():
        func_introduction = """
        设置LocalTensor中的某个值。
        该接口仅在LocalTensor的TPosition为VECIN/VECCALC/VECOUT时支持。
        """

        cpp_signature = """
        **对应的Ascend C函数原型**

            .. code-block:: c++

                template <typename T1> __aicore__ inline __inout_pipe__(S)
                void SetValue(const uint32_t index, const T1 value) const

        """

        param_list = """
        **参数说明**

            - index：LocalTensor索引，单位为元素。
            - value：待设置的数值。
        """

        return func_introduction, cpp_signature, param_list, ""
    
    @staticmethod
    def get_value_docstring():
        func_introduction = """
        获取LocalTensor指定索引的数值。
        该接口仅在LocalTensor的TPosition为VECIN/VECCALC/VECOUT时支持。
        """

        cpp_signature = """
        **对应的Ascend C函数原型**

            .. code-block:: c++

                __aicore__ inline __inout_pipe__(S) PrimType GetValue(const uint32_t index) const

        """

        param_list = """
        **参数说明**

            - index：LocalTensor索引，单位为元素。
        """

        return_list = """
        **返回值说明**

            LocalTensor指定索引的数值，PrimType类型。
        """

        return func_introduction, cpp_signature, param_list, return_list

    @staticmethod
    def set_size_docstring():
        func_introduction = """
        设置当前LocalTensor Size大小。单位为元素。当用户重用local tensor变量且使用长度发生变化的时候，需要使用此接口重新设置Size。
        """

        cpp_signature = """
        **对应的Ascend C函数原型**

            .. code-block:: c++

                __aicore__ inline void SetSize(const uint32_t size)

        """

        param_list = """
        **参数说明**

            - size：元素个数，单位为元素。
        """

        return func_introduction, cpp_signature, param_list, ""

    @staticmethod
    def get_size_docstring():
        func_introduction = """
        获取当前LocalTensor Size大小。
        """

        cpp_signature = """
        **对应的Ascend C函数原型**

            .. code-block:: c++

                __aicore__ inline uint32_t GetSize() const

        """

        param_list = """
        **参数说明**

            无。
        """

        return_list = """
        **返回值说明**

            当前LocalTensor Size大小。单位为元素。
        """

        return func_introduction, cpp_signature, param_list, return_list

    @staticmethod
    def set_user_tag_docstring():
        func_introduction = """
        为Tensor添加用户自定义信息，用户可以根据需要设置对应的Tag。后续可通过GetUserTag获取指定Tensor的Tag信息，并根据Tag信息对Tensor进行相应操作。
        """

        cpp_signature = """
        **对应的Ascend C函数原型**

            .. code-block:: c++

                __aicore__ inline void SetUserTag(const TTagType tag)

        """

        param_list = """
        **参数说明**

            - tag：设置的Tag信息，类型TTagType对应为int32_t。
        """

        return func_introduction, cpp_signature, param_list, ""

    @staticmethod
    def get_user_tag_docstring():
        func_introduction = """
        获取指定Tensor块的Tag信息，用户可以根据Tag信息对Tensor进行不同操作。
        """

        cpp_signature = """
        **对应的Ascend C函数原型**

            .. code-block:: c++

                __aicore__ inline TTagType GetUserTag() const

        """

        param_list = """
        **参数说明**

            无。
        """

        return_list = """
        **返回值说明**

            指定Tensor块的Tag信息。
        """

        return func_introduction, cpp_signature, param_list, return_list
    
    @staticmethod
    def reinterpret_cast_docstring():
        func_introduction = """
        将当前Tensor重解释为用户指定的新类型，转换后的Tensor与原Tensor地址及内容完全相同，Tensor的大小（字节数）保持不变。
        """

        cpp_signature = """
        **对应的Ascend C函数原型**

            .. code-block:: c++

                template <typename CAST_T> 
                __aicore__ inline LocalTensor<CAST_T> ReinterpretCast() const

        """

        param_list = """
        **参数说明**

            - cast_t：用户指定的新类型。
        """

        return_list = """
        **返回值说明**

            重解释转换后的Tensor。
        """
        
        return func_introduction, cpp_signature, param_list, return_list
    
    @staticmethod
    def get_phy_addr_docstring():
        func_introduction = """
        返回LocalTensor的地址或指定偏移量后的地址。
        """

        cpp_signature = """
        **对应的Ascend C函数原型**

            .. code-block:: c++

                __aicore__ inline uint64_t GetPhyAddr() const

            .. code-block:: c++

                __aicore__ inline uint64_t GetPhyAddr(const uint32_t offset) const

        """

        param_list = """
        **参数说明**

            - offset：偏移量。
        """
        
        return_list = """
        **返回值说明**

            LocalTensor的地址或指定偏移量后的地址。
        """
        
        return func_introduction, cpp_signature, param_list, return_list
    
    @staticmethod
    def get_position_docstring():
        func_introduction = """
        获取LocalTensor所在的TPosition逻辑位置，支持TPosition为VECIN、VECOUT、VECCALC、A1、A2、B1、B2、CO1、CO2。
        """

        cpp_signature = """
        **对应的Ascend C函数原型**

            .. code-block:: c++

                __aicore__ inline int32_t GetPosition() const

        """

        param_list = """
        **参数说明**

            无。
        """
        
        return_list = """
        **返回值说明**

            LocalTensor所在的TPosition逻辑位置。
        """
        
        return func_introduction, cpp_signature, param_list, return_list

    @staticmethod
    def get_length_docstring():
        func_introduction = """
        获取LocalTensor数据长度。
        """

        cpp_signature = """
        **对应的Ascend C函数原型**

            .. code-block:: c++

                __aicore__ inline uint32_t GetLength() const

        """

        param_list = """
        **参数说明**

            无。
        """
        
        return_list = """
        **返回值说明**

            LocalTensor数据长度，单位为字节。
        """
        
        return func_introduction, cpp_signature, param_list, return_list
    
    @staticmethod
    def set_shape_info_docstring():
        func_introduction = """
        设置LocalTensor的Shape信息。
        """

        cpp_signature = """
        **对应的Ascend C函数原型**

            .. code-block:: c++

                __aicore__ inline void SetShapeInfo(const ShapeInfo& shapeInfo)

        """

        param_list = """
        **参数说明**

            - shape_info：Shape信息，ShapeInfo结构体类型。
        """
        
        return func_introduction, cpp_signature, param_list, ""
    
    @staticmethod
    def get_shape_info_docstring():
        func_introduction = """
        获取LocalTensor的Shape信息。注意：Shape信息没有默认值，只有通过SetShapeInfo设置过Shape信息后，才可以调用该接口获取正确的Shape信息。
        """

        cpp_signature = """
        **对应的Ascend C函数原型**

            .. code-block:: c++

                __aicore__ inline ShapeInfo GetShapeInfo() const

        """

        param_list = """
        **参数说明**

            无。
        """
        
        return_list = """
        **返回值说明**

            LocalTensor的Shape信息，ShapeInfo结构体类型。
        """
        
        return func_introduction, cpp_signature, param_list, return_list
    
    @staticmethod
    def set_addr_with_offset_docstring():
        func_introduction = """
        设置带有偏移的Tensor地址。用于快速获取定义一个Tensor，同时指定新Tensor相对于旧Tensor首地址的偏移。偏移的长度为旧Tensor的元素个数。
        """

        cpp_signature = """
        **对应的Ascend C函数原型**

            .. code-block:: c++

                template <typename T1>
                __aicore__ inline void SetAddrWithOffset(LocalTensor<T1> &src, uint32_t offset)

        """

        param_list = """
        **参数说明**

            - src：基础地址的Tensor，将该Tensor的地址作为基础地址，设置偏移后的Tensor地址。
            - offset：偏移的长度，单位为元素。
        """
        
        return func_introduction, cpp_signature, param_list, ""
    
    @staticmethod
    def set_buffer_len_docstring():
        func_introduction = """
        设置Buffer长度。当用户调用operator[]函数创建新LocalTensor时，建议调用该接口设置新LocalTensor长度，便于编译器对内存及同步进行自动优化。
        """

        cpp_signature = """
        **对应的Ascend C函数原型**

            .. code-block:: c++

                __aicore__ inline void SetBufferLen(uint32_t dataLen)

        """

        param_list = """
        **参数说明**

            - data_len：Buffer长度，单位为字节。
        """
        
        return func_introduction, cpp_signature, param_list, ""
    
    @staticmethod
    def to_file_docstring():
        func_introduction = """
        只限于CPU调试，将LocalTensor数据Dump到文件中，用于精度调试，文件保存在执行目录。
        """

        cpp_signature = """
        **对应的Ascend C函数原型**

            .. code-block:: c++

                int32_t ToFile(const std::string& fileName) const

        """

        param_list = """
        **参数说明**

            - file_name：保存的文件名称。
        """
        
        return_list = """
        **返回值说明**

            返回0表示数据Dump成功，非0值表示失败。
        """
        
        return func_introduction, cpp_signature, param_list, return_list
    
    @staticmethod
    def print_docstring():
        func_introduction = """
        只限于CPU调试，在调试窗口中打印LocalTensor数据用于精度调试，每一行打印一个DataBlock（32字节）的数据。
        """

        cpp_signature = """
        **对应的Ascend C函数原型**

            .. code-block:: c++

                inline void Print()
            
            .. code-block:: c++

                inline void Print(uint32_t len)

        """

        param_list = """
        **参数说明**

            - len：打印元素个数。
        """
        
        return func_introduction, cpp_signature, param_list, ""


DOC_HANDLERS = {
    "GlobalTensor": {
        "set_global_buffer": GlobalTensorDocstring.set_global_buffer_docstring,
        "get_phy_addr": GlobalTensorDocstring.get_phy_addr_docstring,
        "get_value": GlobalTensorDocstring.get_value_docstring,
        "set_value": GlobalTensorDocstring.set_value_docstring,
        "get_size": GlobalTensorDocstring.get_size_docstring,
        "set_shape_info": GlobalTensorDocstring.set_shape_info_docstring,
        "get_shape_info": GlobalTensorDocstring.get_shape_info_docstring,
        "set_l2_cache_hint": GlobalTensorDocstring.set_l2_cache_hint_docstring,
    },
    "LocalTensor": {
        "set_value": LocalTensorDocstring.set_value_docstring,
        "get_value": LocalTensorDocstring.get_value_docstring,
        "set_size": LocalTensorDocstring.set_size_docstring,
        "get_size": LocalTensorDocstring.get_size_docstring,
        "set_user_tag": LocalTensorDocstring.set_user_tag_docstring,
        "get_user_tag": LocalTensorDocstring.get_user_tag_docstring,
        "reinterpret_cast": LocalTensorDocstring.reinterpret_cast_docstring,
        "get_phy_addr": LocalTensorDocstring.get_phy_addr_docstring,
        "get_position": LocalTensorDocstring.get_position_docstring,
        "get_length": LocalTensorDocstring.get_length_docstring,
        "set_shape_info": LocalTensorDocstring.set_shape_info_docstring,
        "get_shape_info": LocalTensorDocstring.get_shape_info_docstring,
        "set_addr_with_offset": LocalTensorDocstring.set_addr_with_offset_docstring,
        "set_buffer_len": LocalTensorDocstring.set_buffer_len_docstring,
        "to_file": LocalTensorDocstring.to_file_docstring,
        "print": LocalTensorDocstring.print_docstring,
    }
}


def set_tensor_docstring(tensor_name: Optional[str] = None, api_name: Optional[str] = None) -> Callable[[T], T]:
    func_introduction = ""
    cpp_signature = ""
    param_list = ""
    return_list = ""
    if DOC_HANDLERS.get(tensor_name) is None:
        raise RuntimeError(f"Invalid tensor name {tensor_name}")
    if DOC_HANDLERS.get(tensor_name, {}).get(api_name) is None:
        raise RuntimeError(f"Unsupported API [{api_name}] for tensor type [{tensor_name}]")
    handler = DOC_HANDLERS.get(tensor_name, {}).get(api_name)
    func_introduction, cpp_signature, param_list, return_list = handler()
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