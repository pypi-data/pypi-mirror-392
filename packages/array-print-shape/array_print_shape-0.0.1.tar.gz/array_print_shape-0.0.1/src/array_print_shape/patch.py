# torch_repr_shape/patch.py
from __future__ import annotations

import builtins
import os
import sys
from typing import Callable

# 保存原始的 __import__，以及等待懒加载 patch 的模块
_OrigImport = Callable[..., object]

_orig_import: _OrigImport | None = None
_pending_patches: dict[str, Callable[[], None]] = {}


def _install_import_hook() -> None:
    """
    安装一次性的 import hook，用来在首次 import 目标模块时打补丁。
    支持多个模块（例如 torch、numpy）同时挂在 pending 列表里。
    """
    global _orig_import

    if _orig_import is not None:
        # 已经安装过 hook 了
        return

    _orig_import = builtins.__import__

    def _import(name, *args, **kwargs):
        # 先用原始逻辑导入模块
        module = _orig_import(name, *args, **kwargs)
        # 再根据模块名判断是否需要打补丁
        _maybe_patch(name)
        return module

    builtins.__import__ = _import


def _maybe_patch(name: str) -> None:
    """
    如果导入的模块在 pending 列表里，就调用对应的 patch 函数。
    当所有 pending 模块都已 patch 完成后，恢复原始 __import__。
    """
    global _orig_import

    if not _pending_patches:
        return

    # 只看顶层模块名，比如 "numpy.random" -> "numpy"
    top = name.split(".", 1)[0]

    patch_func = _pending_patches.pop(top, None)
    if patch_func is None:
        return

    try:
        patch_func()
    finally:
        # 如果已经没有待处理的模块了，恢复原始 __import__
        if not _pending_patches and _orig_import is not None:
            builtins.__import__ = _orig_import
            _orig_import = None


def _register_lazy_patch(module_name: str, patch_func: Callable[[], None]) -> None:
    """
    注册一个针对 module_name 的懒加载 patch：
    - 若模块已在 sys.modules 中，立刻 patch
    - 否则加入 pending 列表，并安装 import hook
    """
    # 模块已经导入，直接打补丁（由 patch 函数自己保证幂等）
    if module_name in sys.modules:
        patch_func()
        return

    # 还未导入，则登记到 pending 列表
    _pending_patches[module_name] = patch_func
    _install_import_hook()


# ------------------- 对 torch.Tensor 打补丁 -------------------


def enable_torch_shape() -> None:
    """
    启用 torch.Tensor.__repr__ 的 shape 前缀补丁。

    环境变量：
    - DISABLE_TORCH_REPR_SHAPE=1 时，忽略调用。
    """
    if os.environ.get("DISABLE_TORCH_REPR_SHAPE") == "1":
        return

    _register_lazy_patch("torch", _patch_torch)


def _patch_torch() -> None:
    try:
        import torch

        T = torch.Tensor

        # 已经打过补丁就不再重复
        if getattr(T, "__repr__adds_shape__", False):
            return

        orig = T.__repr__

        def _new(self):
            try:
                return f"{{Tensor:{tuple(self.shape)}}} " + orig(self)
            except Exception:
                return orig(self)

        T.__repr__ = _new
        T.__repr__adds_shape__ = True
    except Exception:  # noqa: S110
        # 不影响正常运行
        pass


# ------------------- 对 numpy.ndarray 打补丁 -------------------


def enable_numpy_shape() -> None:
    """
    启用 numpy.ndarray.__repr__ 的 shape 前缀补丁。

    环境变量：
    - DISABLE_NUMPY_REPR_SHAPE=1 时，忽略调用。
    """
    if os.environ.get("DISABLE_NUMPY_REPR_SHAPE") == "1":
        return

    _register_lazy_patch("numpy", _patch_numpy)


def _patch_numpy() -> None:
    try:
        import numpy as np

        A = np.ndarray

        # 已经打过补丁就不再重复
        if getattr(A, "__repr__adds_shape__", False):
            return

        orig = A.__repr__

        def _new(self):
            try:
                return f"{{ndarray:{tuple(self.shape)}}} " + orig(self)
            except Exception:
                return orig(self)

        A.__repr__ = _new
        A.__repr__adds_shape__ = True
    except Exception:  # noqa: S110
        # 不影响正常运行
        pass
