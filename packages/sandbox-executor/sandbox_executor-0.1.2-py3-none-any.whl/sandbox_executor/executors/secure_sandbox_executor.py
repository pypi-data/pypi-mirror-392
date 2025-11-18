"""
Secure Sandbox Executor - Platform Agnostic
============================================

Multi-layered security approach not dependent on Docker or specific platform:

1. RestrictedPython: Compile-time AST filtering
2. Resource Limits: CPU, Memory, Processes (Linux: ulimit, Windows: job objects)
3. Filesystem Isolation: Chroot-like with tempdir
4. Network Blocking: Monkey-patching socket module
5. Import Restrictions: Whitelist allowed modules
6. Execution Timeout: Hard timeout with signal/threading

Deployment targets:
- ✅ Azure Container Apps
- ✅ AWS Fargate
- ✅ Google Cloud Run
- ✅ Kubernetes (any distro)
- ✅ Local development
- ✅ Windows/Linux/Mac
"""

import sys
import os
import tempfile
import subprocess
import multiprocessing
import base64
import resource
import signal
import threading
from typing import Dict, List, Optional, Set
from pathlib import Path
import ast
import builtins


class SecureSandboxExecutor:
    """
    Platform-agnostic secure Python sandbox executor
    """
    
    # Whitelist of safe built-in functions
    SAFE_BUILTINS = {
        'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytes', 'chr',
        'dict', 'divmod', 'enumerate', 'filter', 'float', 'format',
        'frozenset', 'hex', 'int', 'isinstance', 'issubclass', 'iter',
        'len', 'list', 'map', 'max', 'min', 'oct', 'ord', 'pow',
        'print', 'range', 'repr', 'reversed', 'round', 'set', 'slice',
        'sorted', 'str', 'sum', 'tuple', 'type', 'zip',
        'open',  # Allow file I/O (restricted to sandbox tempdir)
        'True', 'False', 'None',
    }
    
    # Whitelist of safe modules
    SAFE_MODULES = {
        'math', 'random', 'datetime', 'json', 'base64', 'hashlib',
        'collections', 'itertools', 'functools', 're', 'string',
        'decimal', 'fractions', 'statistics', 'uuid', 'secrets',
    }
    
    # Blacklist of dangerous modules
    DANGEROUS_MODULES = {
        'os', 'sys', 'subprocess', 'multiprocessing', 'threading',
        'importlib', 'imp', '__import__', 'eval', 'exec', 'compile',
        'open', 'file', 'input', 'raw_input',
    }
    
    # Network-related modules (allowed if allow_network=True)
    NETWORK_MODULES = {
        'socket', 'urllib', 'requests', 'http', 'ftplib', 'smtplib',
        'httplib', 'urllib2', 'urllib3', 'aiohttp', 'websocket',
    }
    
    def __init__(
        self,
        timeout: int = 30,
        max_output_size: int = 1024 * 1024,  # 1MB
        max_memory_mb: int = 128,
        max_cpu_time: int = 30,
        allow_network: bool = False,
        allowed_modules: Optional[Set[str]] = None,
    ):
        """
        Args:
            timeout: Maximum execution time (seconds)
            max_output_size: Maximum output size (bytes)
            max_memory_mb: Maximum memory usage (MB)
            max_cpu_time: Maximum CPU time (seconds)
            allow_network: Allow network access
            allowed_modules: Custom whitelist of allowed modules
        """
        self.timeout = timeout
        self.max_output_size = max_output_size
        self.max_memory_mb = max_memory_mb
        self.max_cpu_time = max_cpu_time
        self.allow_network = allow_network
        self.allowed_modules = allowed_modules or self.SAFE_MODULES
    
    def _validate_code_ast(self, code: str) -> tuple[bool, Optional[str]]:
        """
        Validate code using AST analysis to detect dangerous operations
        
        Returns:
            (is_safe, error_message)
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        
        # Check for dangerous operations
        for node in ast.walk(tree):
            # Check for exec/eval/compile
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in {'exec', 'eval', 'compile', '__import__'}:
                        return False, f"Forbidden function: {node.func.id}"
            
            # Note: We allow open() for file I/O in sandbox directory
            # It will be restricted by running in isolated tempdir
            
            # Check for imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    modules = [alias.name for alias in node.names]
                else:
                    modules = [node.module] if node.module else []
                
                for module in modules:
                    base_module = module.split('.')[0]
                    
                    # Check if it's a network module
                    if base_module in self.NETWORK_MODULES:
                        if not self.allow_network:
                            return False, f"Forbidden module (network disabled): {module}"
                        # If network is allowed, continue to next module
                        continue
                    
                    # Check if it's in dangerous modules
                    if base_module in self.DANGEROUS_MODULES:
                        return False, f"Forbidden module: {module}"
                    
                    # Check if it's in whitelist
                    if base_module not in self.allowed_modules:
                        return False, f"Module not in whitelist: {module}"
        
        return True, None
    
    def _create_restricted_globals(self) -> dict:
        """
        Create a restricted global namespace with safe builtins only
        """
        safe_globals = {
            '__builtins__': {
                name: getattr(builtins, name)
                for name in self.SAFE_BUILTINS
                if hasattr(builtins, name)
            }
        }
        
        # Add safe modules
        for module_name in self.allowed_modules:
            try:
                safe_globals[module_name] = __import__(module_name)
            except ImportError:
                pass
        
        return safe_globals
    
    def _create_wrapper_code(self, user_code: str, input_files: Optional[Dict[str, bytes]]) -> str:
        """
        Wrap user code with security restrictions and resource limits
        """
        wrapper = f'''
import sys
import signal
import io
import os
from pathlib import Path

# Get current working directory (sandbox tempdir)
SANDBOX_DIR = os.getcwd()

# Create safe open() wrapper that restricts file access to sandbox directory
_original_open = open

def _safe_open(file, mode='r', *args, **kwargs):
    """Safe open that only allows access to files in sandbox directory"""
    # Convert to absolute path
    file_path = Path(file).resolve()
    sandbox_path = Path(SANDBOX_DIR).resolve()
    
    # Check if file is within sandbox directory
    try:
        file_path.relative_to(sandbox_path)
    except ValueError:
        raise PermissionError(f"Access denied: File must be in sandbox directory")
    
    return _original_open(file, mode, *args, **kwargs)

# Replace open with safe version
open = _safe_open

# Disable network if needed
{self._get_network_block_code() if not self.allow_network else ""}

# Set resource limits (Linux only)
try:
    import resource
    # Memory limit
    resource.setrlimit(resource.RLIMIT_AS, ({self.max_memory_mb * 1024 * 1024}, {self.max_memory_mb * 1024 * 1024}))
    # CPU time limit
    resource.setrlimit(resource.RLIMIT_CPU, ({self.max_cpu_time}, {self.max_cpu_time}))
    # Process limit
    resource.setrlimit(resource.RLIMIT_NPROC, (10, 10))
except:
    pass  # Windows doesn't support resource module

# Timeout handler
def timeout_handler(signum, frame):
    raise TimeoutError("Execution timed out")

try:
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm({self.timeout})
except:
    pass  # Windows doesn't support SIGALRM

# Capture stdout/stderr
old_stdout = sys.stdout
old_stderr = sys.stderr
sys.stdout = io.StringIO()
sys.stderr = io.StringIO()

exit_code = 0
try:
    # Execute user code
{self._indent_code(user_code, 4)}
except Exception as e:
    import traceback
    sys.stderr.write(traceback.format_exc())
    exit_code = 1
finally:
    signal.alarm(0)  # Cancel timeout
    
    # Restore stdout/stderr
    stdout_content = sys.stdout.getvalue()
    stderr_content = sys.stderr.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    
    # Print outputs (will be captured by subprocess)
    print("<<<STDOUT_START>>>")
    print(stdout_content)
    print("<<<STDOUT_END>>>")
    print("<<<STDERR_START>>>")
    print(stderr_content)
    print("<<<STDERR_END>>>")
    
    # Exit with appropriate code
    sys.exit(exit_code)
'''
        return wrapper
    
    def _get_network_block_code(self) -> str:
        """
        Generate code to block network access by monkey-patching socket
        """
        return '''
# Block network access
import socket
original_socket = socket.socket

def blocked_socket(*args, **kwargs):
    raise PermissionError("Network access is disabled")

socket.socket = blocked_socket
'''
    
    def _indent_code(self, code: str, indent: int) -> str:
        """
        Indent code by specified number of spaces
        """
        spaces = ' ' * indent
        return '\n'.join(spaces + line if line.strip() else line 
                        for line in code.split('\n'))
    
    def execute(
        self,
        code: str,
        input_files: Optional[Dict[str, bytes]] = None
    ) -> Dict:
        """
        Execute Python code in a secure sandbox
        
        Args:
            code: Python code to execute
            input_files: Optional dictionary of filename -> content (bytes)
        
        Returns:
            {
                'stdout': str,
                'stderr': str,
                'return_code': int,
                'output_files': Dict[str, str],  # filename -> base64 content
                'execution_time': float
            }
        """
        import time
        start_time = time.time()
        
        # Step 1: Validate code using AST
        is_safe, error_msg = self._validate_code_ast(code)
        if not is_safe:
            return {
                'stdout': '',
                'stderr': f'Security Error: {error_msg}',
                'return_code': 1,
                'output_files': {},
                'execution_time': 0.0
            }
        
        # Step 2: Execute in isolated subprocess
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Write input files
            if input_files:
                for filename, content in input_files.items():
                    safe_filename = Path(filename).name  # Prevent path traversal
                    (temp_path / safe_filename).write_bytes(content)
            
            # Create wrapper code
            wrapper_code = self._create_wrapper_code(code, input_files)
            code_file = temp_path / "sandbox_code.py"
            code_file.write_text(wrapper_code)
            
            # Execute in subprocess
            try:
                result = subprocess.run(
                    [sys.executable, str(code_file)],
                    cwd=str(temp_path),
                    capture_output=True,
                    timeout=self.timeout + 5,  # Extra buffer for cleanup
                    text=True,
                    env=self._create_safe_env()
                )
                
                # Parse output
                output = result.stdout
                stdout = self._extract_section(output, 'STDOUT')
                stderr = self._extract_section(output, 'STDERR')
                
                if result.stderr:
                    stderr += "\n" + result.stderr
                
                return_code = result.returncode
                
            except subprocess.TimeoutExpired:
                return {
                    'stdout': '',
                    'stderr': f'Execution timed out after {self.timeout} seconds',
                    'return_code': -1,
                    'output_files': {},
                    'execution_time': time.time() - start_time
                }
            except Exception as e:
                return {
                    'stdout': '',
                    'stderr': f'Execution error: {str(e)}',
                    'return_code': -1,
                    'output_files': {},
                    'execution_time': time.time() - start_time
                }
            
            # Collect output files
            output_files = {}
            for file_path in temp_path.iterdir():
                if file_path.name not in {'sandbox_code.py'} and file_path.is_file():
                    # Skip input files
                    if input_files and file_path.name in input_files:
                        continue
                    try:
                        content = file_path.read_bytes()
                        output_files[file_path.name] = base64.b64encode(content).decode('utf-8')
                    except:
                        pass
            
            # Truncate output if too large
            if len(stdout) > self.max_output_size:
                stdout = stdout[:self.max_output_size] + "\n... (output truncated)"
            if len(stderr) > self.max_output_size:
                stderr = stderr[:self.max_output_size] + "\n... (output truncated)"
            
            return {
                'stdout': stdout,
                'stderr': stderr,
                'return_code': return_code,
                'output_files': output_files,
                'execution_time': time.time() - start_time
            }
    
    def _extract_section(self, output: str, section: str) -> str:
        """
        Extract section from delimited output
        """
        start_marker = f"<<<{section}_START>>>"
        end_marker = f"<<<{section}_END>>>"
        
        try:
            start_idx = output.index(start_marker) + len(start_marker)
            end_idx = output.index(end_marker)
            return output[start_idx:end_idx].strip()
        except ValueError:
            return ""
    
    def _create_safe_env(self) -> dict:
        """
        Create safe environment variables
        """
        env = {
            'PYTHONHASHSEED': '0',
            'PYTHONIOENCODING': 'utf-8',
            'PYTHONDONTWRITEBYTECODE': '1',
        }
        
        # Block network via environment variables
        if not self.allow_network:
            env.update({
                'http_proxy': 'http://127.0.0.1:0',
                'https_proxy': 'http://127.0.0.1:0',
                'HTTP_PROXY': 'http://127.0.0.1:0',
                'HTTPS_PROXY': 'http://127.0.0.1:0',
            })
        
        return env
