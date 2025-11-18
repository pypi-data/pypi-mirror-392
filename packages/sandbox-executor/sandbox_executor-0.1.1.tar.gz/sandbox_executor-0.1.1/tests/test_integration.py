"""
Integration tests for Python Code Sandbox
"""
import unittest
import sys
import os
import base64

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.executor_factory import ExecutorFactory


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple components"""
    
    def test_end_to_end_secure_mode(self):
        """Test end-to-end execution in secure mode"""
        executor = ExecutorFactory.create_executor(
            mode="secure",
            timeout=10,
            max_output_size=1024 * 1024,
            allow_network=False
        )
        
        code = """
import math
import json

data = {
    'pi': math.pi,
    'calculation': 2 + 2,
    'message': 'Integration test'
}

print(json.dumps(data, indent=2))
"""
        result = executor.execute(code)
        
        self.assertEqual(result['return_code'], 0)
        self.assertIn('pi', result['stdout'])
        self.assertIn('calculation', result['stdout'])
        self.assertIn('Integration test', result['stdout'])
    
    def test_end_to_end_simple_mode(self):
        """Test end-to-end execution in simple mode"""
        executor = ExecutorFactory.create_executor(
            mode="simple",
            timeout=10,
            max_output_size=1024 * 1024
        )
        
        code = """
numbers = [1, 2, 3, 4, 5]
total = sum(numbers)
print(f"Sum: {total}")
"""
        result = executor.execute(code)
        
        self.assertEqual(result['return_code'], 0)
        self.assertIn('Sum: 15', result['stdout'])
    
    def test_file_processing_pipeline(self):
        """Test complete file processing pipeline"""
        executor = ExecutorFactory.create_executor(mode="secure")
        
        # Create input data
        csv_data = b"name,age\nJohn,30\nJane,25\nBob,35"
        input_files = {'data.csv': csv_data}
        
        code = """
# Read CSV
with open('data.csv', 'r') as f:
    lines = f.readlines()

# Process data
header = lines[0].strip()
data_lines = lines[1:]

# Calculate average age
ages = [int(line.split(',')[1]) for line in data_lines]
avg_age = sum(ages) / len(ages)

# Write results
with open('results.txt', 'w') as f:
    f.write(f"Average age: {avg_age}\\n")
    f.write(f"Total people: {len(ages)}\\n")

print(f"Processed {len(ages)} records")
print(f"Average age: {avg_age}")
"""
        result = executor.execute(code, input_files)
        
        self.assertEqual(result['return_code'], 0)
        self.assertIn('Processed 3 records', result['stdout'])
        self.assertIn('Average age: 30.0', result['stdout'])
        self.assertIn('results.txt', result['output_files'])
        
        # Verify output file
        output_data = base64.b64decode(result['output_files']['results.txt'])
        self.assertIn(b'Average age: 30.0', output_data)
    
    def test_error_recovery(self):
        """Test system handles errors gracefully"""
        executor = ExecutorFactory.create_executor(mode="secure")
        
        # Code that will fail
        code = """
try:
    result = 1 / 0
except ZeroDivisionError as e:
    print(f"Caught error: {e}")
    result = 0

print(f"Result: {result}")
"""
        result = executor.execute(code)
        
        self.assertEqual(result['return_code'], 0)
        self.assertIn('Caught error', result['stdout'])
        self.assertIn('Result: 0', result['stdout'])
    
    def test_multiple_execution_isolation(self):
        """Test that multiple executions are isolated"""
        executor = ExecutorFactory.create_executor(mode="secure")
        
        # First execution
        code1 = """
x = 100
print(f"X = {x}")
"""
        result1 = executor.execute(code1)
        
        # Second execution should not have access to x from first
        code2 = """
try:
    print(f"X from previous: {x}")
except NameError:
    print("X is not defined (good isolation)")
"""
        result2 = executor.execute(code2)
        
        self.assertEqual(result1['return_code'], 0)
        self.assertEqual(result2['return_code'], 0)
        self.assertIn('X is not defined', result2['stdout'])
    
    def test_factory_fallback_mechanism(self):
        """Test factory fallback works correctly"""
        # This should succeed with either mode
        executor, mode = ExecutorFactory.create_with_fallback(
            preferred_mode="secure",
            fallback_mode="simple",
            timeout=10
        )
        
        self.assertIsNotNone(executor)
        self.assertIn(mode, ["secure", "simple"])
        
        # Test execution works
        result = executor.execute("print('Fallback test')")
        self.assertEqual(result['return_code'], 0)


class TestPerformance(unittest.TestCase):
    """Performance and resource tests"""
    
    def test_quick_execution(self):
        """Test quick execution completes fast"""
        import time
        
        executor = ExecutorFactory.create_executor(mode="simple")
        
        start = time.time()
        result = executor.execute("print('Speed test')")
        elapsed = time.time() - start
        
        self.assertEqual(result['return_code'], 0)
        self.assertLess(elapsed, 2.0)  # Should complete in less than 2 seconds
    
    def test_output_size_handling(self):
        """Test handling of output size"""
        executor = ExecutorFactory.create_executor(
            mode="simple",
            max_output_size=1024  # 1KB limit
        )
        
        # Generate output
        code = """
for i in range(100):
    print(f"Line {i}: Some text here")
"""
        result = executor.execute(code)
        
        # Should complete (may truncate output)
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()
