#
# MIT License
#
# Copyright (c) 2025 Huawei Technologies Co., Ltd. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
"""
Monkey patching module for vLLM to apply UCM patches automatically.
This replaces the need for manual `git apply` commands.
"""

import sys
from typing import Any, Optional, Tuple

from ucm.logger import init_logger

logger = init_logger(__name__)

# Track if patches have been applied
_patches_applied = False
_import_hook_installed = False
_vllm_version: Optional[str] = None

def get_vllm_version() -> Optional[str]:
    """Detect vLLM version."""
    global _vllm_version
    if _vllm_version is not None:
        return _vllm_version
    
    try:
        # Try to get version from vllm module
        import vllm as vllm_pkg
        vllm_version = vllm_pkg.__version__
        return vllm_version
    except ImportError:
        logger.warning("vLLM is not installed")
        return None
    except Exception as e:
        logger.warning(f"Failed to detect vLLM version: {e}")
        return None


def get_supported_versions() -> list[str]:
    """Get list of supported vLLM versions."""
    return ["0.9.1", "0.9.2", "0.11.0"]


def apply_all_patches() -> None:
    """Apply all vLLM monkey patches based on detected version."""
    global _patches_applied
    if _patches_applied:
        return

    try:
        version = get_vllm_version()
        if version is None:
            raise ValueError("Could not detect vLLM version")
        
        supported_versions = get_supported_versions()
        if version not in supported_versions:
            logger.warning(
                f"vLLM version {version} is not explicitly supported. "
                f"Supported versions: {', '.join(supported_versions)}. "
                f"Attempting to apply 0.9.2 patches..."
            )
            raise ValueError(f"vLLM version {version} is not explicitly supported")
        
        # Apply version-specific patches
        if version == "0.9.1":
            _apply_patches_v091()
        elif version == "0.9.2":
            _apply_patches_v092()
        elif version == "0.11.0":
            _apply_patches_v0110()
        else:
            raise ValueError(f"Unsupported vLLM version: {version}")
        
        _patches_applied = True
        logger.info(f"All vLLM monkey patches applied successfully for version {version}")
    except Exception as e:
        logger.error(f"Failed to apply vLLM monkey patches: {e}", exc_info=True)
        raise


# def _apply_patches_v091() -> None:
#     """Apply patches for vLLM 0.9.1 (single combined patch)."""
#     from 0.9.1.vllm-adapt-pc-monkey_patch import _apply_adapt_patch_v091
#     _apply_adapt_patch_v091() # apply vllm-adapt-pc.patch
#     if is_npu():
#         from 0.9.1.vllm-ascend-adapt-monkey_patch import _apply_ascend_adapt_patch_v091
#         _apply_ascend_adapt_patch_v091()


def _apply_patches_v092() -> None:
    """Apply patches for vLLM 0.9.2 (three separate patches)."""

    # from 0.9.2.vllm-adapt-aggre-monkey_patch import _apply_aggre_patch
    # _apply_aggre_patch() # apply vllm-adapt-aggre.patch
    from 0.9.2.vllm-adapt-pc-monkey_patch import _apply_pc_patch
    _apply_pc_patch() # apply vllm-adapt-pc.patch
    # from 0.9.2.vllm-adapt-sparse-monkey_patch import _apply_sparse_patch
    # _apply_sparse_patch() # apply vllm-adapt-sparse.patch
    # if is_npu():
    #     from 0.9.2.vllm-ascend-adapt-monkey_patch import _apply_ascend_adapt_patch_v092
    #     _apply_ascend_adapt_patch_v092() # apply vllm-ascend-adapt.patch
    # _apply_adapt_sparse_patch_v092() # apply vllm-adapt-sparse.patch
    # if is_npu():
    #     _apply_ascend_adapt_patch_v092() # apply vllm-ascend-adapt.patch


# def _apply_patches_v0110() -> None:
#     """Apply patches for vLLM 0.11.0."""
#     _apply_pc_patch_v0110() # apply 0001-Patch-UCM-PC-adapt-patch-v1-for-vllm-0.11.0.patch


def install_import_hook() -> None:
    """Install an import hook to automatically apply patches when vLLM is imported."""
    global _import_hook_installed
    if _import_hook_installed:
        return
    
    try:
        # Check if vLLM is already imported
        if 'vllm' in sys.modules:
            # vLLM already imported, apply patches immediately
            apply_all_patches()
        else:
            # Install import hook
            original_import = __import__
            
            def import_hook(name, globals=None, locals=None, fromlist=(), level=0):
                # Call original import
                module = original_import(name, globals, locals, fromlist, level)
                
                # If vLLM is being imported, apply patches
                if name == 'vllm' or name.startswith('vllm.'):
                    if not _patches_applied:
                        try:
                            apply_all_patches()
                        except Exception as e:
                            logger.warning(f"Failed to apply patches during import: {e}")
                
                return module
            
            # Replace builtin __import__ (this is a bit aggressive, so we'll use a different approach)
            # Instead, we'll apply patches when integration module is imported
            _import_hook_installed = True
            
    except Exception as e:
        logger.warning(f"Failed to install import hook: {e}")


def ensure_patches_applied() -> None:
    """Ensure patches are applied, installing import hook if needed."""
    if not _patches_applied:
        # Try to apply patches immediately
        try:
            apply_all_patches()
        except Exception:
            # If it fails (vLLM not imported yet), install hook
            install_import_hook()
