"""
Main executor module - Unified interface for sandbox execution
"""

from typing import Dict, Optional
from dataclasses import dataclass
import base64

from .config import SandboxConfig, ExecutionMode
from .exceptions import SandboxException


@dataclass
class ExecutionResult:
    """Result of code execution"""
    stdout: str
    stderr: str
    return_code: int
    output_files: Dict[str, str]  # filename -> base64 content
    success: bool
    
    @property
    def output(self) -> str:
        """Get combined output (stdout + stderr)"""
        return self.stdout + (("\n" + self.stderr) if self.stderr else "")
    
    def get_file_content(self, filename: str) -> Optional[bytes]:
        """
        Get decoded content of an output file
        
        Args:
            filename: Name of the output file
            
        Returns:
            Decoded file content as bytes, or None if file doesn't exist
        """
        if filename not in self.output_files:
            return None
        return base64.b64decode(self.output_files[filename])


class SandboxExecutor:
    """
    Main executor class - Unified interface for sandbox execution
    
    This class provides a simple interface for executing Python code in a sandbox.
    It automatically selects the appropriate execution backend based on configuration.
    
    Examples:
        Basic usage:
            >>> executor = SandboxExecutor()
            >>> result = executor.execute('print("Hello, World!")')
            >>> print(result.stdout)
            Hello, World!
        
        With configuration:
            >>> config = SandboxConfig(mode=ExecutionMode.SECURE, timeout=60)
            >>> executor = SandboxExecutor.from_config(config)
            >>> result = executor.execute(code)
        
        With files:
            >>> files = {"data.txt": b"Hello, World!"}
            >>> code = "with open('data.txt') as f: print(f.read())"
            >>> result = executor.execute(code, input_files=files)
    """
    
    def __init__(
        self,
        mode: ExecutionMode = ExecutionMode.SECURE,
        timeout: int = 30,
        allow_network: bool = False,
        max_output_size: int = 1024 * 1024,
        max_memory_mb: int = 128,
        max_cpu_time: int = 30,
        allowed_modules: Optional[set] = None,
    ):
        """
        Initialize sandbox executor
        
        Args:
            mode: Execution mode (simple or secure)
            timeout: Maximum execution time in seconds
            allow_network: Allow network access
            max_output_size: Maximum output size in bytes
            max_memory_mb: Maximum memory usage in MB (secure mode)
            max_cpu_time: Maximum CPU time in seconds (secure mode)
            allowed_modules: Custom whitelist of allowed modules (secure mode)
        """
        self.config = SandboxConfig(
            mode=mode,
            timeout=timeout,
            allow_network=allow_network,
            max_output_size=max_output_size,
            max_memory_mb=max_memory_mb,
            max_cpu_time=max_cpu_time,
            allowed_modules=allowed_modules,
        )
        self._backend = self._create_backend()
    
    @classmethod
    def from_config(cls, config: SandboxConfig) -> "SandboxExecutor":
        """
        Create executor from configuration object
        
        Args:
            config: SandboxConfig instance
            
        Returns:
            SandboxExecutor instance
        """
        return cls(
            mode=config.mode,
            timeout=config.timeout,
            allow_network=config.allow_network,
            max_output_size=config.max_output_size,
            max_memory_mb=config.max_memory_mb,
            max_cpu_time=config.max_cpu_time,
            allowed_modules=config.allowed_modules,
        )
    
    @classmethod
    def from_env(cls) -> "SandboxExecutor":
        """
        Create executor from environment variables
        
        Returns:
            SandboxExecutor instance configured from environment
        """
        config = SandboxConfig.from_env()
        return cls.from_config(config)
    
    def _create_backend(self):
        """Create appropriate backend based on execution mode"""
        if self.config.mode == ExecutionMode.SIMPLE:
            from .executors.sandbox_executor import SandboxExecutor as SimpleExecutor
            return SimpleExecutor(
                timeout=self.config.timeout,
                max_output_size=self.config.max_output_size,
                allow_network=self.config.allow_network,
            )
        elif self.config.mode == ExecutionMode.SECURE:
            from .executors.secure_sandbox_executor import SecureSandboxExecutor
            return SecureSandboxExecutor(
                timeout=self.config.timeout,
                max_output_size=self.config.max_output_size,
                allow_network=self.config.allow_network,
                max_memory_mb=self.config.max_memory_mb,
                max_cpu_time=self.config.max_cpu_time,
                allowed_modules=self.config.allowed_modules,
            )
        else:
            raise ValueError(f"Unknown execution mode: {self.config.mode}")
    
    def execute(
        self,
        code: str,
        input_files: Optional[Dict[str, bytes]] = None
    ) -> ExecutionResult:
        """
        Execute Python code in sandbox
        
        Args:
            code: Python code to execute
            input_files: Optional dictionary mapping filename -> file content (bytes)
            
        Returns:
            ExecutionResult with stdout, stderr, return_code, and output_files
            
        Raises:
            ExecutionTimeoutError: If execution exceeds timeout
            SecurityViolationError: If code violates security policies
            CodeValidationError: If code fails validation
        """
        try:
            # Execute using backend
            result_dict = self._backend.execute(code, input_files)
            
            # Convert to ExecutionResult
            return ExecutionResult(
                stdout=result_dict.get("stdout", ""),
                stderr=result_dict.get("stderr", ""),
                return_code=result_dict.get("return_code", 0),
                output_files=result_dict.get("output_files", {}),
                success=result_dict.get("return_code", 0) == 0,
            )
        except Exception as e:
            # Wrap any exception in SandboxException if not already
            if isinstance(e, SandboxException):
                raise
            raise SandboxException(f"Execution failed: {str(e)}") from e
    
    def validate_code(self, code: str) -> tuple[bool, Optional[str]]:
        """
        Validate code without executing it
        
        Args:
            code: Python code to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if hasattr(self._backend, '_validate_code_ast'):
            return self._backend._validate_code_ast(code)
        
        # Simple validation for simple mode
        try:
            compile(code, '<string>', 'exec')
            return True, None
        except SyntaxError as e:
            return False, f"Syntax error at line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, str(e)
