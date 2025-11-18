"""
Unit tests for SandboxExecutor
"""
import unittest
import sys
import os
import base64

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.sandbox_executor.executors.sandbox_executor import SandboxExecutor


class TestSandboxExecutor(unittest.TestCase):
    """Test cases for SandboxExecutor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.executor = SandboxExecutor(timeout=5, max_output_size=1024 * 1024)
    
    def test_simple_print(self):
        """Test simple print statement"""
        code = "print('Hello, World!')"
        result = self.executor.execute(code)
        
        self.assertEqual(result['stdout'], "Hello, World!\n")
        self.assertEqual(result['stderr'], "")
        self.assertEqual(result['return_code'], 0)
    
    def test_multiple_prints(self):
        """Test multiple print statements"""
        code = """
print('Line 1')
print('Line 2')
print('Line 3')
"""
        result = self.executor.execute(code)
        
        self.assertIn("Line 1", result['stdout'])
        self.assertIn("Line 2", result['stdout'])
        self.assertIn("Line 3", result['stdout'])
        self.assertEqual(result['return_code'], 0)
    
    def test_calculation(self):
        """Test basic calculations"""
        code = """
result = 2 + 2
print(f"2 + 2 = {result}")
"""
        result = self.executor.execute(code)
        
        self.assertIn("2 + 2 = 4", result['stdout'])
        self.assertEqual(result['return_code'], 0)
    
    def test_error_handling(self):
        """Test error handling"""
        code = "print(1/0)"  # Division by zero
        result = self.executor.execute(code)
        
        self.assertNotEqual(result['return_code'], 0)
        self.assertIn("ZeroDivisionError", result['stderr'])
    
    def test_syntax_error(self):
        """Test syntax error handling"""
        code = "print('missing quote"
        result = self.executor.execute(code)
        
        self.assertNotEqual(result['return_code'], 0)
        self.assertTrue(len(result['stderr']) > 0)
    
    def test_timeout(self):
        """Test timeout enforcement"""
        executor = SandboxExecutor(timeout=2)
        code = """
import time
time.sleep(10)
print('Should not reach here')
"""
        result = executor.execute(code)
        
        # Should timeout
        self.assertNotEqual(result['return_code'], 0)
    
    def test_read_input_file(self):
        """Test reading input files"""
        input_data = b"Hello from file"
        input_files = {'input.txt': input_data}
        
        code = """
with open('input.txt', 'r') as f:
    content = f.read()
print(content)
"""
        result = self.executor.execute(code, input_files)
        
        self.assertIn("Hello from file", result['stdout'])
        self.assertEqual(result['return_code'], 0)
    
    def test_write_output_file(self):
        """Test writing output files"""
        code = """
with open('output.txt', 'w') as f:
    f.write('Output data')
"""
        result = self.executor.execute(code)
        
        self.assertEqual(result['return_code'], 0)
        self.assertIn('output.txt', result['output_files'])
        
        # Decode and check content
        output_data = base64.b64decode(result['output_files']['output.txt'])
        self.assertEqual(output_data.decode(), 'Output data')
    
    def test_multiple_files(self):
        """Test multiple input and output files"""
        input_files = {
            'file1.txt': b'Content 1',
            'file2.txt': b'Content 2'
        }
        
        code = """
with open('file1.txt', 'r') as f:
    content1 = f.read()
with open('file2.txt', 'r') as f:
    content2 = f.read()

with open('combined.txt', 'w') as f:
    f.write(content1 + ' + ' + content2)
"""
        result = self.executor.execute(code, input_files)
        
        self.assertEqual(result['return_code'], 0)
        self.assertIn('combined.txt', result['output_files'])
        
        combined_data = base64.b64decode(result['output_files']['combined.txt'])
        self.assertEqual(combined_data.decode(), 'Content 1 + Content 2')
    
    def test_standard_library_import(self):
        """Test importing standard library modules"""
        code = """
import math
import json
import datetime

print(f"Pi: {math.pi}")
print(json.dumps({'key': 'value'}))
print(str(datetime.datetime.now().year))
"""
        result = self.executor.execute(code)
        
        self.assertEqual(result['return_code'], 0)
        self.assertIn("Pi: 3.14", result['stdout'])
        self.assertIn("key", result['stdout'])


class TestSandboxExecutorConfiguration(unittest.TestCase):
    """Test configuration options"""
    
    def test_custom_timeout(self):
        """Test custom timeout value"""
        executor = SandboxExecutor(timeout=10)
        self.assertEqual(executor.timeout, 10)
    
    def test_custom_max_output_size(self):
        """Test custom max output size"""
        executor = SandboxExecutor(max_output_size=512 * 1024)
        self.assertEqual(executor.max_output_size, 512 * 1024)
    
    def test_allow_network_flag(self):
        """Test allow network flag"""
        executor1 = SandboxExecutor(allow_network=True)
        executor2 = SandboxExecutor(allow_network=False)
        
        self.assertTrue(executor1.allow_network)
        self.assertFalse(executor2.allow_network)


if __name__ == '__main__':
    unittest.main()
