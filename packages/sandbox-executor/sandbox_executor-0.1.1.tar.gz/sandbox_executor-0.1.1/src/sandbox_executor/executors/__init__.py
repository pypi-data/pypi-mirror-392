"""
Executors Package - Sandbox Execution Strategies
=================================================

This package contains different execution strategies for running Python code in sandboxed environments:

- SandboxExecutor: Simple subprocess-based execution (basic isolation)
- SecureSandboxExecutor: Multi-layered security with platform-agnostic features
"""

from .sandbox_executor import SandboxExecutor
from .secure_sandbox_executor import SecureSandboxExecutor

__all__ = [
    'SandboxExecutor',
    'SecureSandboxExecutor'
]
