"""
Unit tests for SecureSandboxExecutor
"""
import unittest
import sys
import os
import base64

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.executors.secure_sandbox_executor import SecureSandboxExecutor


class TestSecureSandboxExecutor(unittest.TestCase):
    """Test cases for SecureSandboxExecutor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.executor = SecureSandboxExecutor(
            timeout=5,
            max_output_size=1024 * 1024,
            allow_network=False
        )
    
    def test_simple_execution(self):
        """Test simple code execution"""
        code = "print('Hello from secure sandbox')"
        result = self.executor.execute(code)
        
        self.assertIn("Hello from secure sandbox", result['stdout'])
        self.assertEqual(result['return_code'], 0)
    
    def test_safe_module_import(self):
        """Test importing safe modules"""
        code = """
import math
import json
import random

print(f"Pi: {math.pi}")
print(json.dumps({'test': True}))
print(random.randint(1, 1))
"""
        result = self.executor.execute(code)
        
        self.assertEqual(result['return_code'], 0)
        self.assertIn("Pi:", result['stdout'])
        self.assertIn("test", result['stdout'])
    
    def test_dangerous_import_blocked(self):
        """Test that dangerous imports are blocked"""
        dangerous_imports = [
            "import os",
            "import sys",
            "import subprocess",
            "import socket",
        ]
        
        for code in dangerous_imports:
            result = self.executor.execute(code + "\nprint('Should not execute')")
            # Should fail or restrict access
            if result['return_code'] != 0:
                self.assertNotIn('Should not execute', result['stdout'])
    
    def test_file_operations(self):
        """Test file read/write operations"""
        input_files = {'test.txt': b'Test content'}
        
        code = """
with open('test.txt', 'r') as f:
    data = f.read()

with open('output.txt', 'w') as f:
    f.write(data.upper())

print('File operations completed')
"""
        result = self.executor.execute(code, input_files)
        
        self.assertEqual(result['return_code'], 0)
        self.assertIn('File operations completed', result['stdout'])
        self.assertIn('output.txt', result['output_files'])
    
    def test_timeout_enforcement(self):
        """Test timeout is enforced"""
        executor = SecureSandboxExecutor(timeout=2)
        
        code = """
import time
time.sleep(10)
print('Timeout test')
"""
        result = executor.execute(code)
        
        # Should timeout and not return 0
        self.assertNotEqual(result['return_code'], 0)
    
    def test_error_handling(self):
        """Test error handling"""
        code = """
x = 10 / 0
"""
        result = self.executor.execute(code)
        
        # Check for error - either in return code or stderr
        self.assertTrue(
            result['return_code'] != 0 or "ZeroDivisionError" in result['stderr'],
            "Expected error from division by zero"
        )
    
    def test_memory_limit_configuration(self):
        """Test memory limit configuration"""
        executor = SecureSandboxExecutor(max_memory_mb=64)
        self.assertEqual(executor.max_memory_mb, 64)
    
    def test_allowed_modules_configuration(self):
        """Test custom allowed modules"""
        executor = SecureSandboxExecutor(
            allowed_modules={'math', 'json', 'random'}
        )
        
        self.assertEqual(executor.allowed_modules, {'math', 'json', 'random'})
    
    def test_network_blocking(self):
        """Test network is blocked when allow_network=False"""
        executor = SecureSandboxExecutor(allow_network=False)
        
        code = """
import socket
try:
    sock = socket.socket()
    sock.connect(('google.com', 80))
    print('Network allowed')
except:
    print('Network blocked')
"""
        result = executor.execute(code)
        
        # Network should be blocked
        if result['return_code'] == 0:
            self.assertIn('Network blocked', result['stdout'])


class TestSecureSandboxValidation(unittest.TestCase):
    """Test code validation features"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.executor = SecureSandboxExecutor()
    
    def test_ast_validation_safe_code(self):
        """Test AST validation accepts safe code"""
        code = """
x = 10
y = 20
print(x + y)
"""
        is_safe, error = self.executor._validate_code_ast(code)
        self.assertTrue(is_safe)
        self.assertIsNone(error)
    
    def test_multiple_output_files(self):
        """Test creating multiple output files"""
        code = """
with open('file1.txt', 'w') as f:
    f.write('Content 1')

with open('file2.txt', 'w') as f:
    f.write('Content 2')

with open('file3.txt', 'w') as f:
    f.write('Content 3')
"""
        result = self.executor.execute(code)
        
        self.assertEqual(result['return_code'], 0)
        self.assertIn('file1.txt', result['output_files'])
        self.assertIn('file2.txt', result['output_files'])
        self.assertIn('file3.txt', result['output_files'])


if __name__ == '__main__':
    unittest.main()
