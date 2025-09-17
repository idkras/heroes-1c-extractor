module.exports = {
  apps: [{
    name: 'mcp-server',
    script: '[standards .md]/platform/mcp_server/src/mcp_server.py',
    interpreter: 'python3',
    instances: 4,
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'development',
      ENVIRONMENT: 'development'
    },
    env_production: {
      NODE_ENV: 'production',
      ENVIRONMENT: 'production'
    },
    // Logging
    log_file: '/var/log/mcp_server/pm2.log',
    out_file: '/var/log/mcp_server/out.log',
    error_file: '/var/log/mcp_server/error.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',

    // Performance
    max_memory_restart: '1G',
    node_args: '--max-old-space-size=1024',

    // Monitoring
    watch: false,
    ignore_watch: ['node_modules', 'logs'],

    // Restart policy
    autorestart: true,
    max_restarts: 10,
    min_uptime: '10s',

    // Health check
    health_check_grace_period: 3000,
    health_check_fatal_exceptions: true,

    // Security
    uid: 'mcp-server',
    gid: 'mcp-server',

    // Environment variables
    env_file: './config/production.env'
  }],

  deploy: {
    production: {
      user: 'mcp-server',
      host: 'localhost',
      ref: 'origin/main',
      repo: 'git@github.com:heroes-advising/mcp-server.git',
      path: '/opt/mcp-server',
      'pre-deploy-local': '',
      'post-deploy': 'npm install && pm2 reload ecosystem.config.js --env production',
      'pre-setup': ''
    }
  }
};
