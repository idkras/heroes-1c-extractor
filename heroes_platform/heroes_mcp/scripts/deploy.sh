#!/bin/bash

# Production Deployment Script for MCP Server
# Usage: ./deploy.sh [systemd|pm2]

set -e

DEPLOYMENT_TYPE=${1:-systemd}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 Starting MCP Server Production Deployment..."
echo "Deployment type: $DEPLOYMENT_TYPE"
echo "Project root: $PROJECT_ROOT"

# Check if running as root for systemd deployment
if [ "$DEPLOYMENT_TYPE" = "systemd" ] && [ "$EUID" -ne 0 ]; then
    echo "❌ Systemd deployment requires root privileges"
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
sudo mkdir -p /var/log/mcp_server
sudo mkdir -p /var/cache/mcp_server
sudo mkdir -p /opt/mcp-server

# Create user and group
echo "👤 Creating user and group..."
if ! id "mcp-server" &>/dev/null; then
    sudo useradd -r -s /bin/false -d /opt/mcp-server mcp-server
fi

# Set permissions
echo "🔐 Setting permissions..."
sudo chown -R mcp-server:mcp-server /var/log/mcp_server
sudo chown -R mcp-server:mcp-server /var/cache/mcp-server
sudo chown -R mcp-server:mcp-server /opt/mcp-server

# Copy files to production location
echo "📋 Copying files..."
sudo cp -r "$PROJECT_ROOT"/* /opt/mcp-server/
sudo chown -R mcp-server:mcp-server /opt/mcp-server

# Install dependencies
echo "📦 Installing dependencies..."
cd /opt/mcp-server
sudo -u mcp-server pip3 install -r requirements.txt 2>/dev/null || echo "No requirements.txt found"

# Configure environment
echo "⚙️ Configuring environment..."
if [ -f "$PROJECT_ROOT/config/production.env" ]; then
    sudo cp "$PROJECT_ROOT/config/production.env" /opt/mcp-server/config/
fi

# Deploy based on type
if [ "$DEPLOYMENT_TYPE" = "systemd" ]; then
    echo "🔧 Deploying with systemd..."

    # Copy systemd service
    sudo cp "$PROJECT_ROOT/systemd/mcp-server.service" /etc/systemd/system/

    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable mcp-server
    sudo systemctl start mcp-server

    # Check status
    echo "📊 Checking service status..."
    sudo systemctl status mcp-server --no-pager

elif [ "$DEPLOYMENT_TYPE" = "pm2" ]; then
    echo "🔧 Deploying with PM2..."

    # Install PM2 if not present
    if ! command -v pm2 &> /dev/null; then
        echo "📦 Installing PM2..."
        npm install -g pm2
    fi

    # Start with PM2
    cd /opt/mcp-server
    pm2 start ecosystem.config.js --env production

    # Save PM2 configuration
    pm2 save
    pm2 startup

    # Check status
    echo "📊 Checking PM2 status..."
    pm2 status

else
    echo "❌ Unknown deployment type: $DEPLOYMENT_TYPE"
    echo "Supported types: systemd, pm2"
    exit 1
fi

# Test deployment
echo "🧪 Testing deployment..."
sleep 5

# Test basic functionality
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | \
    python3 /opt/mcp-server/src/mcp_server.py > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Deployment test successful!"
else
    echo "❌ Deployment test failed!"
    exit 1
fi

# Show monitoring information
echo "📊 Monitoring information:"
echo "Logs: /var/log/mcp_server/"
echo "Cache: /var/cache/mcp_server/"
echo "Configuration: /opt/mcp-server/config/"

if [ "$DEPLOYMENT_TYPE" = "systemd" ]; then
    echo "Service: sudo systemctl status mcp-server"
    echo "Logs: sudo journalctl -u mcp-server -f"
elif [ "$DEPLOYMENT_TYPE" = "pm2" ]; then
    echo "Status: pm2 status"
    echo "Logs: pm2 logs mcp-server"
fi

echo "🎉 Production deployment completed successfully!"
