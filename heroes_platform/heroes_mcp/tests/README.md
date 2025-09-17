# Tests Directory

This directory contains all tests for the Heroes MCP Server.

## Overview

Tests follow the Testing Pyramid approach with unit tests, integration tests, and end-to-end tests.

## Test Structure

- **unit/** - Unit tests for individual components
- **integration/** - Integration tests for workflow interactions
- **e2e/** - End-to-end tests for complete workflows
- **manual/** - Manual test cases and scenarios

## Running Tests

```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run integration tests only
make test-integration

# Run with coverage
make coverage
```

## Test Standards

- All tests should be independent
- Tests should be deterministic
- Use fixtures for test data
- Aim for ≥90% code coverage
- Include property-based tests with Hypothesis

## Manual Testing

For manual testing scenarios, see the `manual/` directory for test cases that require human verification.
