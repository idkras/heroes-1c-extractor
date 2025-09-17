# Unit Tests Directory

This directory contains unit tests for individual components.

## Overview

Unit tests focus on testing individual functions, classes, and modules in isolation.

## Structure

- Test files follow the pattern `test_*.py`
- Each test file corresponds to a specific module
- Tests use pytest framework

## Running Tests

```bash
# Run all unit tests
pytest tests/unit/

# Run specific test file
pytest tests/unit/test_workflows.py

# Run with coverage
pytest tests/unit/ --cov=src
```

## Test Standards

- Tests should be independent
- Use fixtures for test data
- Mock external dependencies
- Aim for high coverage
