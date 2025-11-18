import subprocess
import sys
import os
import tempfile
import base64
import shutil
from typing import Dict, List, Optional
from pathlib import Path


class SandboxExecutor:
    """
    Execute Python code in a sandbox environment with timeout and resource limits
    """
    
    def __init__(
        self, 
        timeout: int = 30, 
        max_output_size: int = 1024 * 1024,
        allow_network: bool = False
    ):
        """
        Args:
            timeout: Maximum execution time allowed (seconds)
            max_output_size: Maximum output size (bytes)
            allow_network: Allow internet access (default: False)
        """
        self.timeout = timeout
        self.max_output_size = max_output_size
        self.allow_network = allow_network
    
    def execute(
        self, 
        code: str, 
        input_files: Optional[Dict[str, bytes]] = None
    ) -> Dict:
        """
        Execute Python code and return results
        
        Args:
            code: Python code to execute
            input_files: Dictionary mapping filename -> file content (bytes)
        
        Returns:
            Dict containing stdout, stderr, and output_files (base64)
        """
        # Create temporary directory for execution
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Write code to file
            code_file = temp_path / "user_code.py"
            code_file.write_text(code)
            
            # Write input files if provided
            if input_files:
                for filename, content in input_files.items():
                    file_path = temp_path / filename
                    file_path.write_bytes(content)
            
            # Prepare environment variables
            env = os.environ.copy()
            
            # If network is not allowed, disable network operations
            if not self.allow_network:
                # Disable network by setting environment variables
                env['http_proxy'] = 'http://127.0.0.1:0'
                env['https_proxy'] = 'http://127.0.0.1:0'
                env['HTTP_PROXY'] = 'http://127.0.0.1:0'
                env['HTTPS_PROXY'] = 'http://127.0.0.1:0'
                env['no_proxy'] = ''
                env['NO_PROXY'] = ''
            
            # Execute code
            try:
                result = subprocess.run(
                    [sys.executable, str(code_file)],
                    cwd=str(temp_path),
                    capture_output=True,
                    timeout=self.timeout,
                    text=True,
                    env=env
                )
                
                stdout = result.stdout
                stderr = result.stderr
                return_code = result.returncode
                
                # Limit output size
                if len(stdout) > self.max_output_size:
                    stdout = stdout[:self.max_output_size] + "\n... (output truncated)"
                if len(stderr) > self.max_output_size:
                    stderr = stderr[:self.max_output_size] + "\n... (output truncated)"
                
            except subprocess.TimeoutExpired:
                stdout = ""
                stderr = f"Error: Execution timed out after {self.timeout} seconds"
                return_code = -1
            except Exception as e:
                stdout = ""
                stderr = f"Error: {str(e)}"
                return_code = -1
            
            # Collect output files (except code file and input files)
            output_files = {}
            input_filenames = set(input_files.keys()) if input_files else set()
            input_filenames.add("user_code.py")
            
            for file_path in temp_path.iterdir():
                if file_path.is_file() and file_path.name not in input_filenames:
                    try:
                        file_content = file_path.read_bytes()
                        # Convert to base64
                        base64_content = base64.b64encode(file_content).decode('utf-8')
                        output_files[file_path.name] = base64_content
                    except Exception as e:
                        stderr += f"\nWarning: Could not read output file {file_path.name}: {str(e)}"
            
            return {
                "stdout": stdout,
                "stderr": stderr,
                "return_code": return_code,
                "output_files": output_files
            }
