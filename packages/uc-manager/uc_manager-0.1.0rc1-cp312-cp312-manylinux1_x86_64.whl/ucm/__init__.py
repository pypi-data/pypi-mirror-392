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
vLLM integration module for Unified Cache Management.

This module automatically applies patches to vLLM when imported,
eliminating the need for manual `git apply` commands.
"""

# Auto-apply patches when this module is imported
try:
    from ucm.integration.vllm.patch.apply_patch import ensure_patches_applied

    ensure_patches_applied()
except Exception as e:
    # Don't fail if patches can't be applied - might be running in environment without vLLM
    import warnings

    warnings.warn(
        f"Failed to apply vLLM patches: {e}. "
        f"If you're using vLLM, ensure it's installed and patches are compatible."
    )

from ucm.integration.vllm.uc_connector import UnifiedCacheConnectorV1

__all__ = ["UnifiedCacheConnectorV1"]
