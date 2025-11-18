"""
Configuration module for Sandbox Executor
"""

import os
from enum import Enum
from typing import Optional, Set
from pydantic import BaseModel, Field, field_validator


class ExecutionMode(str, Enum):
    """Execution modes for the sandbox"""
    SIMPLE = "simple"      # Basic subprocess isolation
    SECURE = "secure"      # Multi-layered security


class SandboxConfig(BaseModel):
    """Configuration for sandbox executor"""
    
    mode: ExecutionMode = Field(
        default=ExecutionMode.SECURE,
        description="Execution mode (simple or secure)"
    )
    
    timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Maximum execution time in seconds"
    )
    
    allow_network: bool = Field(
        default=False,
        description="Allow network access during code execution"
    )
    
    max_output_size: int = Field(
        default=1024 * 1024,  # 1MB
        ge=1024,
        le=10 * 1024 * 1024,  # 10MB max
        description="Maximum output size in bytes"
    )
    
    max_memory_mb: int = Field(
        default=128,
        ge=16,
        le=2048,
        description="Maximum memory usage in MB (secure mode only)"
    )
    
    max_cpu_time: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Maximum CPU time in seconds (secure mode only)"
    )
    
    allowed_modules: Optional[Set[str]] = Field(
        default=None,
        description="Custom whitelist of allowed modules (secure mode only)"
    )
    
    @field_validator("mode", mode="before")
    @classmethod
    def validate_mode(cls, v):
        """Validate and convert mode to ExecutionMode"""
        if isinstance(v, str):
            return ExecutionMode(v.lower())
        return v
    
    @classmethod
    def from_env(cls, prefix: str = "SANDBOX_") -> "SandboxConfig":
        """
        Create configuration from environment variables
        
        Environment variables:
            SANDBOX_MODE: Execution mode (simple/secure)
            SANDBOX_TIMEOUT: Timeout in seconds
            SANDBOX_ALLOW_NETWORK: Allow network (true/false)
            SANDBOX_MAX_OUTPUT_SIZE: Max output size in bytes
            SANDBOX_MAX_MEMORY_MB: Max memory in MB
            SANDBOX_MAX_CPU_TIME: Max CPU time in seconds
        
        Example:
            config = SandboxConfig.from_env()
        """
        return cls(
            mode=os.getenv(f"{prefix}MODE", "secure"),
            timeout=int(os.getenv(f"{prefix}TIMEOUT", "30")),
            allow_network=os.getenv(f"{prefix}ALLOW_NETWORK", "false").lower() in ("true", "1", "yes"),
            max_output_size=int(os.getenv(f"{prefix}MAX_OUTPUT_SIZE", str(1024 * 1024))),
            max_memory_mb=int(os.getenv(f"{prefix}MAX_MEMORY_MB", "128")),
            max_cpu_time=int(os.getenv(f"{prefix}MAX_CPU_TIME", "30")),
        )
    
    class Config:
        use_enum_values = True
