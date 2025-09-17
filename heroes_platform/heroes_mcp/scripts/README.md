# Scripts Directory

This directory contains utility scripts for the Heroes MCP Server.

## Overview

Scripts provide automation for documentation, monitoring, and maintenance tasks.

## Available Scripts

### Documentation Scripts
- **generate_api_docs.py** - Automatically generates API documentation from code
- **update_dependencies_matrix.py** - Updates the dependencies matrix
- **validate_docs.py** - Validates documentation quality and coverage

### Monitoring Scripts
- **enhanced_log_monitor.py** - Enhanced log monitoring and analysis
- **health_check.py** - Server health monitoring
- **check_critical_issues.py** - Critical issue detection
- **final_alert_check.py** - Final alert verification
- **analyze_logs.py** - Log analysis and reporting

## Usage

```bash
# Generate documentation
python3 scripts/generate_api_docs.py

# Update dependencies matrix
python3 scripts/update_dependencies_matrix.py

# Validate documentation
python3 scripts/validate_docs.py

# Monitor logs
python3 scripts/enhanced_log_monitor.py
```

## Integration

These scripts are integrated with the Makefile:

```bash
make docs-generate  # Runs generate_api_docs.py
make docs-validate  # Runs validate_docs.py
make deps          # Runs update_dependencies_matrix.py
```

## Adding New Scripts

1. Create a new Python file in this directory
2. Add proper docstrings and error handling
3. Update this README with usage instructions
4. Add to Makefile if needed
