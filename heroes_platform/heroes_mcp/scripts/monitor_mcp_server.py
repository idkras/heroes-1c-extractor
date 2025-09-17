#!/usr/bin/env python3
"""
MCP Server Continuous Monitoring

Система непрерывного мониторинга MCP сервера с автоматическим восстановлением.
"""

import asyncio
import logging
import signal
import sys
import time
from pathlib import Path
from typing import Any

from .mcp_health_check import MCPHealthMonitor  # type: ignore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("mcp_monitor.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class MCPContinuousMonitor:
    """Continuous monitoring system for MCP server"""

    def __init__(self, check_interval: int = 60, max_failures: int = 3):
        self.check_interval = check_interval
        self.max_failures = max_failures
        self.monitor = MCPHealthMonitor(
            Path(__file__).parent.parent / "src" / "mcp_server.py"
        )
        self.running = False
        self.stats = {
            "total_checks": 0,
            "successful_checks": 0,
            "failed_checks": 0,
            "recovery_attempts": 0,
            "start_time": time.time(),
        }

    async def start_monitoring(self):
        """Start continuous monitoring"""
        logger.info("Starting MCP server continuous monitoring")
        self.running = True

        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        try:
            while self.running:
                await self._monitoring_cycle()
                await asyncio.sleep(self.check_interval)
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        finally:
            await self._shutdown()

    async def _monitoring_cycle(self):
        """Single monitoring cycle"""
        self.stats["total_checks"] += 1

        try:
            # Perform health check
            health_result = await self.monitor.check_server_health()

            if health_result["status"] == "healthy":
                self.stats["successful_checks"] += 1
                logger.info("Health check PASSED - Server is healthy")

                # Reset failure count on success
                if self.monitor.failure_count > 0:
                    logger.info("Server recovered - failure count reset to 0")
                    self.monitor.failure_count = 0

            else:
                self.stats["failed_checks"] += 1
                logger.warning(f"Health check FAILED - {health_result}")

                # Check if recovery is needed
                if self.monitor.failure_count >= self.max_failures:
                    await self._attempt_recovery()

        except Exception as e:
            self.stats["failed_checks"] += 1
            logger.error(f"Monitoring cycle error: {e}")

    async def _attempt_recovery(self):
        """Attempt to recover the server"""
        self.stats["recovery_attempts"] += 1
        logger.warning(
            f"Attempting server recovery (attempt {self.stats['recovery_attempts']})"
        )

        try:
            # Try to restart the server
            await self._restart_server()

            # Wait a bit and check again
            await asyncio.sleep(10)

            recovery_check = await self.monitor.check_server_health()
            if recovery_check["status"] == "healthy":
                logger.info("Server recovery SUCCESSFUL")
                self.monitor.failure_count = 0
            else:
                logger.error("Server recovery FAILED")

        except Exception as e:
            logger.error(f"Recovery attempt failed: {e}")

    async def _restart_server(self):
        """Restart the MCP server"""
        logger.info("Restarting MCP server...")

        # This would typically involve:
        # 1. Stopping the current server process
        # 2. Starting a new server process
        # 3. Waiting for it to initialize

        # For now, we'll just log the restart attempt
        # In a real implementation, this would manage the actual server process

        logger.info("MCP server restart initiated")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    async def _shutdown(self):
        """Clean shutdown"""
        logger.info("Shutting down MCP monitor")

        # Log final statistics
        uptime = time.time() - self.stats["start_time"]
        success_rate = (
            (self.stats["successful_checks"] / self.stats["total_checks"]) * 100
            if self.stats["total_checks"] > 0
            else 0
        )

        logger.info(
            f"Final stats - Uptime: {uptime:.1f}s, Success rate: {success_rate:.1f}%, "
            f"Recovery attempts: {self.stats['recovery_attempts']}"
        )

    def get_status(self) -> dict[str, Any]:
        """Get current monitoring status"""
        uptime = time.time() - self.stats["start_time"]
        success_rate = (
            (self.stats["successful_checks"] / self.stats["total_checks"]) * 100
            if self.stats["total_checks"] > 0
            else 0
        )

        return {
            "running": self.running,
            "uptime": uptime,
            "success_rate": success_rate,
            "stats": self.stats,
            "last_check": self.monitor.last_check,
        }


async def main():
    """Main entry point"""
    # Parse command line arguments
    check_interval = 60  # Default: check every 60 seconds
    max_failures = 3  # Default: attempt recovery after 3 failures

    if len(sys.argv) > 1:
        check_interval = int(sys.argv[1])
    if len(sys.argv) > 2:
        max_failures = int(sys.argv[2])

    monitor = MCPContinuousMonitor(
        check_interval=check_interval, max_failures=max_failures
    )
    await monitor.start_monitoring()


if __name__ == "__main__":
    asyncio.run(main())
