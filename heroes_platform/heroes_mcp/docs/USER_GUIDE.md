# MCP Server User Guide

## Overview
The Heroes Advising Platform MCP Server provides 10 workflow commands for managing standards, hypotheses, JTBD scenarios, TDD, QA, dependencies, Ghost integration, migration, and performance monitoring.

## Quick Start

### 1. Installation
```bash
# Clone the repository
git clone <repository-url>
cd heroes-advising-project

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp config/production.env.example config/production.env
# Edit production.env with your settings
```

### 2. Running the Server
```bash
# Development mode
python3 "[standards .md]/platform/mcp_server/src/mcp_server.py"

# Production mode
python3 "[standards .md]/platform/mcp_server/src/mcp_server.py" --production
```

### 3. Testing Connection
```bash
# Test basic functionality
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | python3 "[standards .md]/platform/mcp_server/src/mcp_server.py"
```

## Available Commands

### 1. Standards Management
**Purpose:** Manage and validate standards in the system

**Commands:**
- `get_standards` - List all available standards
- `validate_standard` - Validate a specific standard
- `create_standard` - Create a new standard

**Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "standards-management",
    "arguments": {
      "command": "get_standards",
      "arguments": {}
    }
  }
}
```

### 2. HeroesGPT Workflow
**Purpose:** Execute HeroesGPT Landing Analysis Standard v1.8

**Commands:**
- `execute_heroes_workflow` - Execute complete workflow
- `deep_segment_research` - Perform deep segment research
- `activating_knowledge` - Generate activating knowledge
- `unified_table` - Create unified table methodology
- `expert_review` - Perform expert review

**Example:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "heroes-gpt-workflow",
    "arguments": {
      "command": "execute_heroes_workflow",
      "arguments": {
        "landing_url": "https://example.com",
        "segments": ["quality_focused", "comfort_seekers"]
      }
    }
  }
}
```

### 3. Hypothesis Workflow
**Purpose:** Manage hypotheses with scientific methodology

**Commands:**
- `form_hypothesis` - Create a new hypothesis
- `falsify_or_confirm` - Test hypothesis validity
- `list_hypotheses` - List all hypotheses

### 4. JTBD Workflow
**Purpose:** Manage Jobs-To-Be-Done scenarios

**Commands:**
- `build_jtbd` - Build JTBD scenarios
- `create_jtbd_scenarios` - Create new scenarios
- `list_jtbd` - List all scenarios

### 5. TDD Workflow
**Purpose:** Manage Test-Driven Development processes

**Commands:**
- `create_tdd_plan` - Create TDD plan
- `execute_tdd_cycle` - Execute TDD cycle
- `validate_tdd` - Validate TDD implementation

### 6. QA Workflow
**Purpose:** Manage Quality Assurance processes

**Commands:**
- `create_qa_plan` - Create QA plan
- `execute_qa_tests` - Execute QA tests
- `validate_qa` - Validate QA results

### 7. Dependency Management
**Purpose:** Manage system dependencies

**Commands:**
- `dependency_management` - Manage dependencies
- `validate_dependencies` - Validate dependency structure
- `monitor_dependencies` - Monitor dependency health

### 8. Ghost Integration
**Purpose:** Manage Ghost CMS integration

**Commands:**
- `ghost_publish_analysis` - Publish analysis to Ghost
- `ghost_publish_document` - Publish document to Ghost
- `ghost_integration` - Manage integration settings

### 9. Migration Workflow
**Purpose:** Manage system migrations

**Commands:**
- `migrate_legacy_to_modern` - Migrate from legacy to modern system
- `update_registry_legacy_deprecated` - Mark legacy as deprecated
- `validate_migration_success` - Validate migration
- `rollback_migration_if_needed` - Rollback if needed

### 10. Performance Monitor
**Purpose:** Monitor system performance

**Commands:**
- `get_performance_report` - Get performance report
- `save_metrics` - Save performance metrics

## Configuration

### Environment Variables
```bash
# Server Configuration
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=3000
MCP_SERVER_WORKERS=4
MCP_SERVER_TIMEOUT=30

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/mcp_server/mcp_server.log

# Performance Configuration
MAX_CONCURRENT_REQUESTS=100
REQUEST_TIMEOUT=30
MEMORY_LIMIT=512MB
CPU_LIMIT=2
```

### Production Setup
1. **Environment Configuration:**
   ```bash
   cp config/production.env.example config/production.env
   # Edit production.env with your settings
   ```

2. **Process Management:**
   ```bash
   # Using PM2
   npm install -g pm2
   pm2 start ecosystem.config.js

   # Using systemd
   sudo cp systemd/mcp-server.service /etc/systemd/system/
   sudo systemctl enable mcp-server
   sudo systemctl start mcp-server
   ```

3. **Logging Setup:**
   ```bash
   sudo mkdir -p /var/log/mcp_server
   sudo chown $USER:$USER /var/log/mcp_server
   ```

## Monitoring and Logging

### Performance Monitoring
The system automatically tracks:
- Command execution times
- Success/failure rates
- Resource usage
- Error rates

### Logging
Logs are stored in JSON format with:
- Timestamp
- Log level
- Module and function
- Error details
- Performance metrics

### Health Checks
```bash
# Check server health
curl http://localhost:3000/health

# Check performance metrics
curl http://localhost:3000/metrics
```

## Troubleshooting

### Common Issues

1. **Server won't start:**
   - Check environment variables
   - Verify port availability
   - Check log files

2. **Commands failing:**
   - Check command syntax
   - Verify required arguments
   - Check error logs

3. **Performance issues:**
   - Monitor resource usage
   - Check cache statistics
   - Review performance logs

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python3 "[standards .md]/platform/mcp_server/src/mcp_server.py"
```

### Log Analysis
```bash
# View recent logs
tail -f /var/log/mcp_server/mcp_server.log

# Search for errors
grep '"level":"ERROR"' /var/log/mcp_server/mcp_server.log

# Performance analysis
grep '"event_type":"performance_metric"' /var/log/mcp_server/mcp_server.log
```

## Security

### Authentication
- API key authentication (optional)
- Rate limiting enabled
- Request validation

### Rate Limiting
- 100 requests per hour per IP
- Configurable limits
- Automatic blocking of abusive IPs

### Data Protection
- All sensitive data encrypted
- Secure file permissions
- Regular security audits

## Backup and Recovery

### Backup Strategy
- Daily automated backups
- 7-day retention policy
- Encrypted backup storage

### Recovery Procedures
1. Stop the server
2. Restore from backup
3. Verify data integrity
4. Restart the server

### Manual Backup
```bash
# Create backup
tar -czf backup-$(date +%Y%m%d).tar.gz /var/cache/mcp_server /var/log/mcp_server

# Restore backup
tar -xzf backup-20250818.tar.gz -C /
```

## Support

### Getting Help
- Check this documentation
- Review log files
- Contact support team

### Reporting Issues
When reporting issues, include:
- Error messages
- Log files
- System configuration
- Steps to reproduce

### Feature Requests
Submit feature requests through:
- GitHub issues
- Support email
- Team meetings

## Version History

### v1.0.0 (2025-08-18)
- Initial production release
- 10 workflow commands
- Performance monitoring
- Structured logging
- Production deployment

### Upcoming Features
- Advanced caching strategies
- Real-time monitoring dashboard
- API rate limiting improvements
- Enhanced security features
