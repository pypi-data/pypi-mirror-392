"""
Sandbox Executor - Secure Python Code Execution Library
========================================================

A flexible Python sandbox execution library that supports multiple execution modes:
- Simple: Basic subprocess isolation
- Secure: Multi-layered security with resource limits

Perfect for integrating with AI agents, code execution platforms, and debugging tools.

Quick Start
-----------

Basic usage::

    from sandbox_executor import SandboxExecutor, ExecutionMode
    
    executor = SandboxExecutor(
        mode=ExecutionMode.SECURE,
        timeout=30,
        allow_network=False
    )
    
    result = executor.execute('''
        def hello(name):
            return f"Hello, {name}!"
        
        print(hello("World"))
    ''')
    
    print(result.stdout)  # "Hello, World!"
    print(result.success) # True

With configuration::

    from sandbox_executor import SandboxExecutor, SandboxConfig, ExecutionMode
    
    config = SandboxConfig(
        mode=ExecutionMode.SECURE,
        timeout=60,
        allow_network=False,
        max_memory_mb=256,
        max_output_size=2 * 1024 * 1024  # 2MB
    )
    
    executor = SandboxExecutor.from_config(config)
    result = executor.execute(code)

For more examples, see the examples/ directory.
"""

from .config import SandboxConfig, ExecutionMode
from .executor import SandboxExecutor, ExecutionResult
from .client import SandboxClient, ClientConfig
from .exceptions import (
    SandboxException,
    ExecutionTimeoutError,
    SecurityViolationError,
    CodeValidationError,
)

__version__ = "0.1.0"
__author__ = "dinhhungitsoft"
__all__ = [
    # Main classes
    "SandboxExecutor",
    "SandboxClient",
    "ExecutionResult",
    
    # Configuration
    "SandboxConfig",
    "ClientConfig",
    "ExecutionMode",
    
    # Exceptions
    "SandboxException",
    "ExecutionTimeoutError",
    "SecurityViolationError",
    "CodeValidationError",
]
