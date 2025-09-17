# Integration Tests Directory

This directory contains integration tests for workflow interactions.

## Overview

Integration tests verify that different components work together correctly.

## Structure

- Test workflow interactions
- Test MCP protocol compliance
- Test end-to-end scenarios

## Running Tests

```bash
# Run all integration tests
pytest tests/integration/

# Run specific integration test
pytest tests/integration/test_workflow_interactions.py
```

## Test Focus

- Workflow communication
- Data flow between components
- Error handling across boundaries
- Performance under load
