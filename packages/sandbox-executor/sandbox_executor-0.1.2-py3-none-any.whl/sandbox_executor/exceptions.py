"""
Custom exceptions for Sandbox Executor
"""


class SandboxException(Exception):
    """Base exception for all sandbox-related errors"""
    pass


class ExecutionTimeoutError(SandboxException):
    """Raised when code execution exceeds the timeout limit"""
    
    def __init__(self, timeout: int):
        self.timeout = timeout
        super().__init__(f"Code execution timed out after {timeout} seconds")


class SecurityViolationError(SandboxException):
    """Raised when code violates security policies"""
    
    def __init__(self, message: str, violation_type: str = "unknown"):
        self.violation_type = violation_type
        super().__init__(f"Security violation ({violation_type}): {message}")


class CodeValidationError(SandboxException):
    """Raised when code fails validation checks"""
    
    def __init__(self, message: str, line: int = None):
        self.line = line
        line_info = f" at line {line}" if line else ""
        super().__init__(f"Code validation failed{line_info}: {message}")


class ResourceLimitError(SandboxException):
    """Raised when resource limits are exceeded"""
    
    def __init__(self, resource: str, limit: str):
        self.resource = resource
        self.limit = limit
        super().__init__(f"Resource limit exceeded: {resource} (limit: {limit})")


class NetworkAccessError(SandboxException):
    """Raised when network access is attempted but not allowed"""
    
    def __init__(self):
        super().__init__("Network access is not allowed in this sandbox")
