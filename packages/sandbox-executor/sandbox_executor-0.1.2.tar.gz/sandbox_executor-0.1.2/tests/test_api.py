"""
Unit tests for FastAPI endpoints
"""
import unittest
from fastapi.testclient import TestClient
import sys
import os
import base64

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.main import app


class TestAPIEndpoints(unittest.TestCase):
    """Test cases for API endpoints"""
    
    def setUp(self):
        """Set up test client"""
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Test root endpoint returns health status"""
        response = self.client.get("/")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertIn('version', data)
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get("/health")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('execution_mode', data)
        self.assertIn('config', data)
    
    def test_execute_simple_code(self):
        """Test executing simple code"""
        response = self.client.post("/execute", json={
            "code": "print('Hello, API!')"
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("Hello, API!", data['stdout'])
        self.assertEqual(data['return_code'], 0)
    
    def test_execute_with_calculation(self):
        """Test executing code with calculations"""
        response = self.client.post("/execute", json={
            "code": """
result = 5 + 3
print(f"Result: {result}")
"""
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("Result: 8", data['stdout'])
        self.assertEqual(data['return_code'], 0)
    
    def test_execute_with_error(self):
        """Test executing code that raises an error"""
        response = self.client.post("/execute", json={
            "code": "x = 1 / 0"
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertNotEqual(data['return_code'], 0)
        self.assertIn("ZeroDivisionError", data['stderr'])
    
    def test_execute_with_timeout(self):
        """Test custom timeout parameter"""
        response = self.client.post("/execute", json={
            "code": "print('Quick execution')",
            "timeout": 5
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['return_code'], 0)
    
    def test_execute_with_files(self):
        """Test executing code with input files"""
        input_content = b"Test file content"
        input_base64 = base64.b64encode(input_content).decode()
        
        response = self.client.post("/execute", json={
            "code": """
with open('input.txt', 'r') as f:
    content = f.read()
print(f"Read: {content}")

with open('output.txt', 'w') as f:
    f.write(content.upper())
""",
            "files": {
                "input.txt": input_base64
            }
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("Test file content", data['stdout'])
        self.assertIn('output.txt', data['output_files'])
        
        # Verify output file content
        output_data = base64.b64decode(data['output_files']['output.txt'])
        self.assertEqual(output_data.decode(), "TEST FILE CONTENT")
    
    def test_execute_with_invalid_base64(self):
        """Test executing with invalid base64 in files"""
        response = self.client.post("/execute", json={
            "code": "print('test')",
            "files": {
                "test.txt": "invalid_base64!!!"
            }
        })
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid base64", response.json()['detail'])
    
    def test_execute_with_network_flag(self):
        """Test allow_network parameter"""
        response = self.client.post("/execute", json={
            "code": "print('Network test')",
            "allow_network": False
        })
        
        self.assertEqual(response.status_code, 200)
    
    def test_timeout_validation(self):
        """Test timeout must be within valid range"""
        # Too small
        response = self.client.post("/execute", json={
            "code": "print('test')",
            "timeout": 0
        })
        self.assertEqual(response.status_code, 422)
        
        # Too large
        response = self.client.post("/execute", json={
            "code": "print('test')",
            "timeout": 500
        })
        self.assertEqual(response.status_code, 422)
    
    def test_missing_code_parameter(self):
        """Test request without code parameter fails"""
        response = self.client.post("/execute", json={})
        self.assertEqual(response.status_code, 422)
    
    def test_execute_with_multipart(self):
        """Test execute-with-files endpoint"""
        response = self.client.post(
            "/execute-with-files",
            data={
                "code": "print('Multipart test')",
                "timeout": "10"
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("Multipart test", data['stdout'])


class TestAPIValidation(unittest.TestCase):
    """Test API input validation"""
    
    def setUp(self):
        """Set up test client"""
        self.client = TestClient(app)
    
    def test_code_is_required(self):
        """Test that code field is required"""
        response = self.client.post("/execute", json={
            "timeout": 30
        })
        self.assertEqual(response.status_code, 422)
    
    def test_timeout_range_validation(self):
        """Test timeout must be between 1 and 300"""
        # Valid range
        response = self.client.post("/execute", json={
            "code": "print('test')",
            "timeout": 150
        })
        self.assertEqual(response.status_code, 200)
    
    def test_files_optional(self):
        """Test files parameter is optional"""
        response = self.client.post("/execute", json={
            "code": "print('No files')"
        })
        self.assertEqual(response.status_code, 200)
    
    def test_allow_network_boolean(self):
        """Test allow_network accepts boolean"""
        for value in [True, False]:
            response = self.client.post("/execute", json={
                "code": "print('test')",
                "allow_network": value
            })
            self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
