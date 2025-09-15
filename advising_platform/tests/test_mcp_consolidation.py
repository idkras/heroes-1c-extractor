#!/usr/bin/env python3
"""
TDD Red Phase Tests for MCP Consolidation
Following TDD Documentation Standard v2.0: Real Data Analysis → Test Creation → Implementation

JTBD: As a developer, I want to test MCP consolidation functionality
to ensure all Python modules are accessible via enhanced orchestrator.
"""

import pytest
import sys
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from advising_platform.src.mcp.mcp_orchestrator import MCPOrchestrator

class TestMCPConsolidation:
    """Test enhanced MCP Orchestrator with consolidated functionality"""
    
    def test_mcp_protocol_compliance(self):
        """Test that orchestrator supports MCP protocol standards"""
        orchestrator = MCPOrchestrator()
        
        # This should fail initially - testing MCP protocol support
        assert orchestrator.supports_mcp_protocol() == True
        
        # Test MCP command registration
        assert len(orchestrator.get_mcp_commands()) > 0
        
        # Test required MCP commands are available
        required_commands = [
            'form-hypothesis',
            'build-jtbd', 
            'write-prd',
            'analyze-landing',
            'validate-compliance'
        ]
        
        available_commands = orchestrator.get_mcp_commands()
        for cmd in required_commands:
            assert cmd in available_commands, f"Missing required MCP command: {cmd}"
    
    def test_python_modules_direct_import(self):
        """Test direct Python module imports without spawning"""
        orchestrator = MCPOrchestrator()
        
        # Test with real module from python_backends
        test_modules = [
            'standards_navigator',
            'compliance_checker',
            'create_incident',
            'standards_resolver'
        ]
        
        for module_name in test_modules:
            # This should fail initially - testing direct module imports
            result = orchestrator.call_python_module(module_name, {'test': True})
            assert result is not None, f"Failed to import module: {module_name}"
            assert 'success' in result
    
    def test_atomic_operations_registry_compliance(self):
        """Test Registry Standard v4.7 atomic operations support"""
        orchestrator = MCPOrchestrator()
        
        # This should fail initially - testing atomic operations
        assert orchestrator.supports_atomic_operations() == True
        
        # Test reflection checkpoint functionality
        test_data = {"test": "data"}
        assert orchestrator.reflection_checkpoint("test_step", test_data) is not None
    
    def test_command_gap_analysis(self):
        """Test that command gap (44 vs 8) is resolved"""
        orchestrator = MCPOrchestrator()
        
        # README claims 44 commands, current has 8
        available_commands = orchestrator.get_mcp_commands()
        
        # Should have at least 10 commands after consolidation
        assert len(available_commands) >= 10, f"Expected >=10 commands, got {len(available_commands)}"
    
    def test_python_backend_integration(self):
        """Test integration with all Python backend modules"""
        orchestrator = MCPOrchestrator()
        
        # Test real modules from python_backends directory
        backend_modules = [
            'mcp_dashboard_logger',
            'standards_integration', 
            'workflow_completion_triggers',
            'tdd_pyramid_validator'
        ]
        
        for module in backend_modules:
            # Test module accessibility
            module_path = Path(f"advising_platform/src/mcp/python_backends/{module}.py")
            assert module_path.exists(), f"Module not found: {module}"
            
            # Test module can be imported and called
            result = orchestrator.call_python_module(module, {'action': 'test'})
            assert result is not None, f"Failed to call module: {module}"
    
    def test_tdd_workflow_integration(self):
        """Test TDD workflow steps are properly integrated"""
        orchestrator = MCPOrchestrator()
        
        # Test 8-step TDD workflow is available
        workflow_steps = orchestrator.get_workflow_steps()
        expected_steps = [
            'form_hypothesis',
            'build_jtbd',
            'write_prd', 
            'red_phase_tests',
            'implement_feature',
            'run_tests',
            'evaluate_outcome',
            'falsify_or_confirm'
        ]
        
        for step in expected_steps:
            assert step in workflow_steps, f"Missing workflow step: {step}"
    
    def test_real_data_processing(self):
        """Test with real data from existing system"""
        orchestrator = MCPOrchestrator()
        
        # Use real input data structure
        real_input = {
            "operation": "analyze-landing",
            "url": "https://example.com",
            "standard": "heroesGPT",
            "timestamp": datetime.now().isoformat()
        }
        
        # Test orchestrator can process real data
        result = orchestrator.execute_full_cycle(json.dumps(real_input))
        
        assert result is not None
        assert "workflow_id" in result
        assert "steps_executed" in result
    
    def test_zero_deletion_policy(self):
        """Test that all existing files are preserved"""
        # Test existing modules are still accessible
        existing_modules = [
            'advising_platform/src/mcp/python_backends/compliance_checker.py',
            'advising_platform/src/mcp/python_backends/standards_navigator.py',
            'advising_platform/src/mcp/python_backends/create_incident.py',
            'advising_platform/src/mcp/bridge/chat_api.py',
            'advising_platform/src/mcp/bridge/chat_bridge.py',
            'advising_platform/src/mcp/standards_mcp_server.js'
        ]
        
        for module_path in existing_modules:
            assert Path(module_path).exists(), f"File should be preserved: {module_path}"
    
    def test_all_python_backends_integration(self):
        """Test integration with ALL Python backend modules from python_backends/ directory"""
        orchestrator = MCPOrchestrator()
        
        # Complete list of modules from ls advising_platform/src/mcp/python_backends/ (22 total)
        all_backend_modules = [
            'add_mcp_command',
            'compliance_checker', 
            'create_incident',
            'create_task',
            'documentation_indexer',
            'heroes_workflow',
            'ilya_review_challenge', 
            'live_mcp_chat_integration',
            'mcp_dashboard_logger',
            'mcp_registry_scanner',
            'protocol_handler',
            'readme_updater',
            'replit_domain_detector',
            'standards_integration',
            'standards_navigator',
            'standards_resolver',
            'standards_suggester',
            'tdd_pyramid_validator',
            'update_standard',
            'validate_compliance',
            'validate_standard_compliance',
            'workflow_completion_triggers'
        ]
        
        # Test each module can be accessed via orchestrator
        failed_modules = []
        successful_modules = []
        
        for module_name in all_backend_modules:
            try:
                # Check file exists (относительно корня проекта)
                project_root = Path(__file__).parent.parent.parent
                module_path = project_root / f"advising_platform/src/mcp/python_backends/{module_name}.py"
                assert module_path.exists(), f"Module file not found: {module_name} at {module_path}"
                
                # Test module can be imported and called via orchestrator
                result = orchestrator.call_python_module(module_name, {'action': 'test', 'validate': True})
                
                if result is not None:
                    successful_modules.append(module_name)
                else:
                    failed_modules.append(f"{module_name}: returned None")
                    
            except Exception as e:
                failed_modules.append(f"{module_name}: {str(e)}")
        
        # Report results 
        print(f"✅ Successfully integrated modules ({len(successful_modules)}): {successful_modules}")
        if failed_modules:
            print(f"❌ Failed modules ({len(failed_modules)}): {failed_modules}")
        
        # CRITICAL: All modules from python_backends/ should be accessible
        assert len(failed_modules) == 0, f"Failed to integrate modules: {failed_modules}"
        assert len(successful_modules) >= 22, f"Expected 22+ modules, got {len(successful_modules)}"
    
    def test_performance_vs_spawning(self):
        """Test performance improvement vs child_process spawning"""
        orchestrator = MCPOrchestrator()
        
        # Test direct import is faster than spawning
        import time
        
        start_time = time.time()
        result = orchestrator.call_python_module('standards_navigator', {'test': True})
        direct_time = time.time() - start_time
        
        # Direct import should be faster than 100ms (spawning baseline)
        assert direct_time < 0.1, f"Direct import too slow: {direct_time}s"
        assert result is not None

if __name__ == "__main__":
    # Run tests to see current failures (Red Phase)
    pytest.main([__file__, "-v"])