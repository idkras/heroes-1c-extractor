# Documentation Directory

This directory contains all documentation for the Heroes MCP Server.

## Overview

The documentation is automatically generated and maintained using scripts in the `scripts/` directory.

## Structure

- **api/** - Automatically generated API documentation
  - `index.md` - API documentation index
  - `workflows.md` - Workflow documentation
  - `tools.md` - MCP tools documentation
  - `schemas.md` - Data schemas documentation

- **architecture/** - Architectural documentation
  - `dependencies_matrix.md` - Project dependencies matrix
  - `workflow_diagram.md` - Workflow architecture diagrams
  - `system_overview.md` - System overview

- **guides/** - User guides and tutorials

## Auto-Generation

Documentation is automatically generated using:

```bash
# Generate API documentation
make docs-generate

# Validate documentation quality
make docs-validate

# Update dependencies matrix
make deps
```

## Manual Updates

For manual documentation updates:

1. Edit the relevant markdown files
2. Run validation to check quality
3. Update the documentation strategy if needed

## Quality Standards

- Docstring coverage should be ≥95%
- No broken links
- All examples should be tested
- Documentation should be up-to-date
