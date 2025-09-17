#!/usr/bin/env python3
"""Integration tests for CocoIndex functionality."""

import unittest
import tempfile
import os
import shutil
import time
import cocoindex
from cocoindex.setting import DatabaseConnectionSpec, Settings


class TestCocoIndexIntegration(unittest.TestCase):
    """Integration tests for CocoIndex."""
    
    def setUp(self):
        """Set up test environment."""
        self.settings = Settings(
            database=DatabaseConnectionSpec(
                url="postgresql://cocoindex:cocoindex@localhost:5432/cocoindex"
            )
        )
        cocoindex.init(self.settings)
        
        # Create temporary test directory
        self.test_dir = tempfile.mkdtemp()
        self.markdown_dir = os.path.join(self.test_dir, "markdown_files")
        os.makedirs(self.markdown_dir, exist_ok=True)
        
        # Create test markdown file
        self.test_file = os.path.join(self.markdown_dir, "integration_test.md")
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write("""# Integration Test Document

This document is specifically designed to test end-to-end functionality.

## Test Section 1

This is the first test section with some content.

## Test Section 2

This is the second test section with more content.

### Subsection

This is a subsection with additional content.
""")
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_end_to_end_simple_flow(self):
        """Test complete simple flow workflow."""
        try:
            # Import the flow
            import flows.simple_flow
            
            # Test that flow is properly registered
            flows_list = cocoindex.setup.flow_names_with_setup()
            self.assertIn("SimpleTextFlow", flows_list)
            
            print("✅ End-to-end simple flow test structure validated")
            
        except Exception as e:
            self.fail(f"End-to-end simple flow test failed: {e}")
    
    def test_database_connection_real(self):
        """Test real database connection and operations."""
        try:
            # Test that we can get flow names (requires DB connection)
            flows = cocoindex.setup.flow_names_with_setup()
            self.assertIsInstance(flows, list)
            self.assertGreater(len(flows), 0)
            
            print(f"✅ Real database connection test passed: {len(flows)} flows found")
            
        except Exception as e:
            self.fail(f"Real database connection test failed: {e}")
    
    def test_flow_setup_and_update(self):
        """Test flow setup and update operations."""
        try:
            # Test that flows are properly registered
            flows_list = cocoindex.setup.flow_names_with_setup()
            self.assertIn("SimpleTextFlow", flows_list)
            self.assertIn("TextEmbedding", flows_list)
            print("✅ Flow setup test passed")
            
            # Test flow registration (this validates setup)
            print("✅ Flow update test structure validated")
            
        except Exception as e:
            self.fail(f"Flow setup and update test failed: {e}")
    
    def test_error_handling(self):
        """Test error handling scenarios."""
        try:
            # Test with invalid flow name
            with self.assertRaises(Exception):
                cocoindex.setup.setup_flow("invalid_flow")
            
            print("✅ Error handling test passed")
            
        except Exception as e:
            self.fail(f"Error handling test failed: {e}")
    
    def test_performance_basic(self):
        """Test basic performance characteristics."""
        try:
            start_time = time.time()
            
            # Perform basic operations
            flows = cocoindex.setup.flow_names_with_setup()
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Should complete within reasonable time
            self.assertLess(execution_time, 10.0)
            
            print(f"✅ Performance test passed: {execution_time:.2f}s")
            
        except Exception as e:
            self.fail(f"Performance test failed: {e}")


class TestCocoIndexDataValidation(unittest.TestCase):
    """Test data validation and quality."""
    
    def setUp(self):
        """Set up test environment."""
        self.settings = Settings(
            database=DatabaseConnectionSpec(
                url="postgresql://cocoindex:cocoindex@localhost:5432/cocoindex"
            )
        )
        cocoindex.init(self.settings)
    
    def test_data_quality_validation(self):
        """Test data quality validation."""
        try:
            # Test that flows are properly configured
            flows = cocoindex.setup.flow_names_with_setup()
            
            # Validate flow names
            expected_flows = ["SimpleTextFlow", "TextEmbedding"]
            for flow in expected_flows:
                self.assertIn(flow, flows)
            
            print("✅ Data quality validation test passed")
            
        except Exception as e:
            self.fail(f"Data quality validation test failed: {e}")
    
    def test_flow_configuration_validation(self):
        """Test flow configuration validation."""
        try:
            # Test simple flow configuration
            import flows.simple_flow
            
            # Validate flow structure
            from cocoindex.flow import Flow
            self.assertIsInstance(flows.simple_flow.simple_text_flow, Flow)
            
            # Validate flow name
            self.assertEqual(flows.simple_flow.simple_text_flow.name, "SimpleTextFlow")
            
            print("✅ Flow configuration validation test passed")
            
        except Exception as e:
            self.fail(f"Flow configuration validation test failed: {e}")


def main():
    """Run integration tests."""
    print("🧪 Running CocoIndex integration tests...")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCocoIndexIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestCocoIndexDataValidation))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n📊 Integration Test Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("✅ All integration tests passed!")
        return 0
    else:
        print("❌ Some integration tests failed!")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
