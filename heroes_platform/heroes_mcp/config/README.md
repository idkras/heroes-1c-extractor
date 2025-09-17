# Configuration Directory

This directory contains configuration files for the MCP Server.

## Overview

Configuration files define server behavior, logging, and integration settings.

## Files

- **mcp.json** - MCP server configuration
- **telegram_config.example** - Example Telegram configuration
- **logging.conf** - Logging configuration

## Usage

Copy example files and modify for your environment:
```bash
cp telegram_config.example telegram_config.json
```

## Environment Variables

Key environment variables:
- `ENVIRONMENT` - Set to 'production' for production mode
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
