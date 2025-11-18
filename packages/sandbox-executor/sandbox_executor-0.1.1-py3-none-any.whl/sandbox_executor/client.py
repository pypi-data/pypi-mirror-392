"""
Unified Sandbox Client - Local or Remote Execution
===================================================

This client provides a unified interface that can execute code either:
1. Locally (direct execution using the sandbox executor)
2. Remotely (via HTTP API calls to a sandbox server)

The client automatically switches between modes based on whether a server URL is provided.
"""

from typing import Dict, Optional, Union
import base64
from dataclasses import dataclass

from .config import SandboxConfig, ExecutionMode
from .executor import ExecutionResult
from .exceptions import SandboxException


@dataclass
class ClientConfig:
    """Configuration for the unified client"""
    server_url: Optional[str] = None  # If None, runs locally
    timeout: int = 30
    allow_network: bool = False
    mode: ExecutionMode = ExecutionMode.SECURE
    max_memory_mb: int = 128
    max_output_size: int = 1024 * 1024
    
    # API client settings
    api_timeout: int = 60  # HTTP request timeout
    api_key: Optional[str] = None  # Optional API key for authentication


class SandboxClient:
    """
    Unified client for executing Python code locally or remotely.
    
    Examples:
        Local execution:
            >>> client = SandboxClient()
            >>> result = client.execute("print('Hello')")
        
        Remote execution:
            >>> client = SandboxClient(server_url="http://localhost:8000")
            >>> result = client.execute("print('Hello')")
        
        With configuration:
            >>> config = ClientConfig(
            ...     server_url="http://sandbox-api.example.com",
            ...     timeout=60,
            ...     api_key="your-api-key"
            ... )
            >>> client = SandboxClient.from_config(config)
    """
    
    def __init__(
        self,
        server_url: Optional[str] = None,
        timeout: int = 30,
        allow_network: bool = False,
        mode: ExecutionMode = ExecutionMode.SECURE,
        max_memory_mb: int = 128,
        api_timeout: int = 60,
        api_key: Optional[str] = None,
    ):
        """
        Initialize the sandbox client
        
        Args:
            server_url: If provided, uses remote API; if None, executes locally
            timeout: Maximum execution time in seconds
            allow_network: Allow network access during code execution
            mode: Execution mode (simple or secure) - local only
            max_memory_mb: Maximum memory usage in MB - local only
            api_timeout: HTTP request timeout for remote calls
            api_key: Optional API key for authentication
        """
        self.server_url = server_url.rstrip('/') if server_url else None
        self.timeout = timeout
        self.allow_network = allow_network
        self.mode = mode
        self.max_memory_mb = max_memory_mb
        self.api_timeout = api_timeout
        self.api_key = api_key
        
        # Initialize local executor only if running locally
        self._local_executor = None
        if not self.server_url:
            self._init_local_executor()
    
    @classmethod
    def from_config(cls, config: ClientConfig) -> "SandboxClient":
        """Create client from configuration object"""
        return cls(
            server_url=config.server_url,
            timeout=config.timeout,
            allow_network=config.allow_network,
            mode=config.mode,
            max_memory_mb=config.max_memory_mb,
            api_timeout=config.api_timeout,
            api_key=config.api_key,
        )
    
    def _init_local_executor(self):
        """Initialize local executor"""
        from .executor import SandboxExecutor
        self._local_executor = SandboxExecutor(
            mode=self.mode,
            timeout=self.timeout,
            allow_network=self.allow_network,
            max_memory_mb=self.max_memory_mb,
        )
    
    @property
    def is_local(self) -> bool:
        """Check if client is running in local mode"""
        return self.server_url is None
    
    @property
    def is_remote(self) -> bool:
        """Check if client is running in remote mode"""
        return self.server_url is not None
    
    def execute(
        self,
        code: str,
        input_files: Optional[Dict[str, bytes]] = None,
        timeout: Optional[int] = None,
        allow_network: Optional[bool] = None,
    ) -> ExecutionResult:
        """
        Execute Python code either locally or remotely
        
        Args:
            code: Python code to execute
            input_files: Optional dictionary mapping filename -> file content (bytes)
            timeout: Override default timeout for this execution
            allow_network: Override default network setting for this execution
            
        Returns:
            ExecutionResult with stdout, stderr, return_code, and output_files
            
        Raises:
            SandboxException: If execution fails
        """
        if self.is_local:
            return self._execute_local(code, input_files, timeout, allow_network)
        else:
            return self._execute_remote(code, input_files, timeout, allow_network)
    
    def _execute_local(
        self,
        code: str,
        input_files: Optional[Dict[str, bytes]],
        timeout: Optional[int],
        allow_network: Optional[bool],
    ) -> ExecutionResult:
        """Execute code locally"""
        # Override settings if provided
        if timeout is not None or allow_network is not None:
            from .executor import SandboxExecutor
            executor = SandboxExecutor(
                mode=self.mode,
                timeout=timeout or self.timeout,
                allow_network=allow_network if allow_network is not None else self.allow_network,
                max_memory_mb=self.max_memory_mb,
            )
            return executor.execute(code, input_files)
        
        return self._local_executor.execute(code, input_files)
    
    def _execute_remote(
        self,
        code: str,
        input_files: Optional[Dict[str, bytes]],
        timeout: Optional[int],
        allow_network: Optional[bool],
    ) -> ExecutionResult:
        """Execute code via remote API"""
        try:
            import requests
        except ImportError:
            raise SandboxException(
                "requests library is required for remote execution. "
                "Install it with: pip install requests"
            )
        
        # Prepare request payload
        payload = {
            "code": code,
            "timeout": timeout or self.timeout,
            "allow_network": allow_network if allow_network is not None else self.allow_network,
        }
        
        # Encode input files to base64
        if input_files:
            payload["files"] = {
                filename: base64.b64encode(content).decode('utf-8')
                for filename, content in input_files.items()
            }
        
        # Prepare headers
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        # Make API request
        try:
            response = requests.post(
                f"{self.server_url}/execute",
                json=payload,
                headers=headers,
                timeout=self.api_timeout,
            )
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            
            return ExecutionResult(
                stdout=data.get("stdout", ""),
                stderr=data.get("stderr", ""),
                return_code=data.get("return_code", 0),
                output_files=data.get("output_files", {}),
                success=data.get("return_code", 0) == 0,
            )
            
        except requests.exceptions.Timeout:
            raise SandboxException(f"API request timed out after {self.api_timeout} seconds")
        except requests.exceptions.ConnectionError:
            raise SandboxException(f"Failed to connect to server: {self.server_url}")
        except requests.exceptions.HTTPError as e:
            raise SandboxException(f"API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise SandboxException(f"Remote execution failed: {str(e)}") from e
    
    def validate_code(self, code: str) -> tuple[bool, Optional[str]]:
        """
        Validate code without executing it
        
        Args:
            code: Python code to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if self.is_local:
            return self._local_executor.validate_code(code)
        else:
            # For remote, we can only do basic syntax check
            try:
                compile(code, '<string>', 'exec')
                return True, None
            except SyntaxError as e:
                return False, f"Syntax error at line {e.lineno}: {e.msg}"
            except Exception as e:
                return False, str(e)
    
    def health_check(self) -> bool:
        """
        Check if the sandbox is available
        
        Returns:
            True if available, False otherwise
        """
        if self.is_local:
            # Local is always available
            return True
        else:
            # Check remote server
            try:
                import requests
                response = requests.get(
                    f"{self.server_url}/",
                    timeout=5
                )
                return response.status_code == 200
            except:
                return False
    
    def get_mode_info(self) -> Dict[str, Union[str, bool]]:
        """
        Get information about the current execution mode
        
        Returns:
            Dictionary with mode information
        """
        return {
            "execution_type": "local" if self.is_local else "remote",
            "server_url": self.server_url,
            "timeout": self.timeout,
            "allow_network": self.allow_network,
            "mode": self.mode.value if self.is_local else "N/A",
            "max_memory_mb": self.max_memory_mb if self.is_local else "N/A",
        }
    
    def __repr__(self) -> str:
        mode_type = "Local" if self.is_local else f"Remote({self.server_url})"
        return f"SandboxClient({mode_type}, timeout={self.timeout})"
