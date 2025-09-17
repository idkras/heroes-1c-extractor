# Abstract Links Integration Documentation

## Overview

This document describes the integration of abstract links functionality from the advising platform into the MCP server project. The abstract links system provides a way to work with logical references instead of hard-coded file paths, making the system more maintainable and flexible.

## Background

The abstract links system was originally developed in the advising platform (`/Users/ilyakrasinsky/workspace/vscode.projects/heroes.advising.project/advising_platform`) and was integrated into this MCP server project to provide consistent abstract link resolution capabilities.

## Architecture

### Core Components

1. **AbstractLinksResolver** (`src/primitives/abstract_links.py`)
   - Main resolver class for abstract address resolution
   - Handles mapping between logical IDs and physical paths
   - Provides caching and persistence functionality

2. **AbstractLinksWorkflow** (`src/workflows/abstract_links_workflow.py`)
   - MCP workflow wrapper for abstract links functionality
   - Provides standardized interface for MCP tools
   - Handles command routing and response formatting

3. **MCP Server Integration** (`src/mcp_server.py`)
   - Integrated abstract links as a new MCP tool
   - Added workflow specification and tool registration

## Features

### Abstract Address Resolution

The system supports resolving abstract addresses in the format:
- `abstract://standard:task_master` → `[standards .md]/0. core standards/0.0 task master...`
- `abstract://task:todo` → `[todo · incidents]/todo.md`
- `abstract://incident:ai` → `[todo · incidents]/ai.incidents.md`

### Automatic Mapping Discovery

The system automatically scans the standards directory and creates mappings for all markdown files found, extracting logical IDs from filenames.

### Link Conversion

Supports bidirectional conversion between abstract and physical links in text content:
- Physical paths → Abstract links
- Abstract links → Physical paths

### Search and Filtering

Provides search functionality across mappings with filtering by document type.

## Usage

### MCP Tool Commands

The abstract links functionality is available through the MCP server as the `abstract-links` tool with the following commands:

#### 1. resolve_abstract_path
Resolves an abstract address to physical path.

```json
{
  "command": "resolve_abstract_path",
  "abstract_address": "abstract://standard:task_master"
}
```

Response:
```json
{
  "abstract_address": "abstract://standard:task_master",
  "resolved_path": "[standards .md]/0. core standards/0.0 task master 10 may 2226 cet by ilya krasinsky.md",
  "absolute_path": "/path/to/project/standards .md/0. core standards/0.0 task master 10 may 2226 cet by ilya krasinsky.md",
  "success": true
}
```

#### 2. get_mappings
Retrieves mappings, optionally filtered by document type.

```json
{
  "command": "get_mappings",
  "doc_type": "standard"
}
```

#### 3. register_mapping
Registers a new mapping manually.

```json
{
  "command": "register_mapping",
  "logical_id": "standard:new_standard",
  "physical_path": "[standards .md]/new_standard.md",
  "doc_type": "standard",
  "title": "New Standard",
  "description": "Description of the new standard"
}
```

#### 4. convert_links
Converts links in text between abstract and physical formats.

```json
{
  "command": "convert_links",
  "text": "See [Task Master Standard](../../../0. core standards/0.0 task master 10 may 2226 cet by ilya krasinsky.md)",
  "to_abstract": false
}
```

#### 5. get_statistics
Returns statistics about the mappings.

```json
{
  "command": "get_statistics"
}
```

#### 6. refresh_mappings
Refreshes mappings by re-scanning directories.

```json
{
  "command": "refresh_mappings"
}
```

#### 7. search_mappings
Searches mappings by query.

```json
{
  "command": "search_mappings",
  "query": "task",
  "doc_type": "standard",
  "limit": 10
}
```

### Direct API Usage

You can also use the abstract links functionality directly in Python code:

```python
from primitives.abstract_links import get_resolver, resolve_abstract_path

# Get resolver instance
resolver = get_resolver()

# Resolve abstract address
physical_path = resolver.resolve("abstract://standard:task_master")

# Quick resolution function
path = resolve_abstract_path("abstract://task:todo")

# Convert links in text
converted_text = resolver.convert_text_links(text, to_abstract=True)
```

## Configuration

### Cache File

Mappings are cached in `data/abstract_mappings.json` relative to the project root. This file is automatically created and updated by the system.

### Core Mappings

The system includes predefined core mappings for essential files:
- `task:todo` → `[todo · incidents]/todo.md`
- `incident:ai` → `[todo · incidents]/ai.incidents.md`
- `standard:task_master` → Task Master Standard
- `standard:registry` → Registry Standard
- And more...

## Testing

The integration includes comprehensive tests in `tests/test_abstract_links.py` that verify:
- Abstract address resolution
- Workflow functionality
- Link conversion
- Statistics and search

Run tests with:
```bash
python tests/test_abstract_links.py
```

## Integration Details

### File Structure

```
src/
├── primitives/
│   └── abstract_links.py          # Core resolver functionality
├── workflows/
│   └── abstract_links_workflow.py # MCP workflow wrapper
└── mcp_server.py                  # MCP server with integration

tests/
└── test_abstract_links.py         # Integration tests

data/
└── abstract_mappings.json         # Cache file (auto-generated)
```

### MCP Server Integration

The abstract links functionality is integrated into the MCP server through:

1. **Workflow Import**: Added import for `AbstractLinksWorkflow`
2. **Tool Registration**: Added `abstract-links` tool to the tools list
3. **Workflow Specification**: Added workflow specification for lazy loading

### Error Handling

The system includes comprehensive error handling:
- Graceful fallbacks for missing files
- Logging of resolution failures
- Validation of input parameters
- Safe file operations

## Performance

- **Caching**: Mappings are cached in memory and persisted to disk
- **Lazy Loading**: Workflows are loaded only when needed
- **Efficient Scanning**: Directory scanning is optimized to skip archive folders
- **Minimal I/O**: File operations are minimized through caching

## Future Enhancements

Potential improvements for the abstract links system:

1. **Real-time Monitoring**: Watch for file system changes and update mappings automatically
2. **Validation**: Validate that physical paths actually exist
3. **Conflict Resolution**: Handle cases where multiple files could map to the same logical ID
4. **Versioning**: Support for versioned mappings
5. **API Endpoints**: REST API endpoints for external access

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the project structure is correct and Python path includes the src directory
2. **Missing Files**: Check that the standards directory exists and contains markdown files
3. **Permission Issues**: Ensure write permissions for the data directory
4. **Cache Corruption**: Delete `data/abstract_mappings.json` to regenerate mappings

### Debugging

Enable debug logging to see detailed information about mapping operations:

```python
import logging
logging.getLogger('primitives.abstract_links').setLevel(logging.DEBUG)
```

## Conclusion

The abstract links integration provides a robust foundation for working with logical references in the MCP server project. It maintains compatibility with the original advising platform implementation while providing a clean MCP interface for external tools and clients.

The system successfully resolves 91 mappings including 87 standards, demonstrating comprehensive coverage of the project's documentation structure.
