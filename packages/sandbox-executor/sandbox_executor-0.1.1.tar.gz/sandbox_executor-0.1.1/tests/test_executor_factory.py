"""
Unit tests for ExecutorFactory
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.executor_factory import ExecutorFactory


class TestExecutorFactory(unittest.TestCase):
    """Test cases for ExecutorFactory"""
    
    def test_create_secure_executor(self):
        """Test creating secure executor"""
        executor = ExecutorFactory.create_executor(
            mode="secure",
            timeout=30,
            max_output_size=1024 * 1024,
            allow_network=False
        )
        
        self.assertIsNotNone(executor)
        self.assertEqual(executor.timeout, 30)
        self.assertEqual(executor.max_output_size, 1024 * 1024)
        self.assertEqual(executor.allow_network, False)
    
    def test_create_simple_executor(self):
        """Test creating simple executor"""
        executor = ExecutorFactory.create_executor(
            mode="simple",
            timeout=20,
            max_output_size=512 * 1024,
            allow_network=True
        )
        
        self.assertIsNotNone(executor)
        self.assertEqual(executor.timeout, 20)
        self.assertEqual(executor.max_output_size, 512 * 1024)
        self.assertEqual(executor.allow_network, True)
    
    def test_create_executor_case_insensitive(self):
        """Test that mode is case-insensitive"""
        executor1 = ExecutorFactory.create_executor(mode="SECURE")
        executor2 = ExecutorFactory.create_executor(mode="Secure")
        executor3 = ExecutorFactory.create_executor(mode="secure")
        
        self.assertIsNotNone(executor1)
        self.assertIsNotNone(executor2)
        self.assertIsNotNone(executor3)
    
    def test_create_executor_invalid_mode(self):
        """Test creating executor with invalid mode raises ValueError"""
        with self.assertRaises(ValueError) as context:
            ExecutorFactory.create_executor(mode="invalid")
        
        self.assertIn("Unknown execution mode", str(context.exception))
    
    def test_create_with_fallback_success(self):
        """Test create_with_fallback with successful preferred mode"""
        executor, mode = ExecutorFactory.create_with_fallback(
            preferred_mode="secure",
            fallback_mode="simple"
        )
        
        self.assertIsNotNone(executor)
        self.assertEqual(mode, "secure")
    
    def test_create_with_fallback_to_fallback(self):
        """Test create_with_fallback falls back on error"""
        with patch.object(ExecutorFactory, '_create_secure_executor', side_effect=Exception("Test error")):
            executor, mode = ExecutorFactory.create_with_fallback(
                preferred_mode="secure",
                fallback_mode="simple"
            )
            
            self.assertIsNotNone(executor)
            self.assertEqual(mode, "simple")
    
    def test_create_with_custom_kwargs(self):
        """Test creating executor with custom kwargs"""
        executor = ExecutorFactory.create_executor(
            mode="secure",
            timeout=45,
            max_output_size=2048 * 1024,
            allow_network=True,
            max_memory_mb=256,
            max_cpu_time=60
        )
        
        self.assertIsNotNone(executor)
        self.assertEqual(executor.timeout, 45)
        self.assertEqual(executor.max_memory_mb, 256)
        self.assertEqual(executor.max_cpu_time, 60)


if __name__ == '__main__':
    unittest.main()
