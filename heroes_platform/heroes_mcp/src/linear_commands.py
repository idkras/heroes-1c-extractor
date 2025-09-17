"""
Linear MCP Commands
JTBD: Как MCP сервер, я хочу предоставлять команды для работы с Linear,
чтобы обеспечить автоматическое создание и управление задачами через MCP.

Поддерживает:
- Создание задач в Linear
- Создание циклов (релизов)
- Управление командами
- Перемещение задач между циклами
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from heroes_platform.shared.credentials_manager import CredentialsManager

# Import Linear API client
from heroes_platform.src.integrations.linear.linear_api_client import LinearAPIClient

logger = logging.getLogger(__name__)


class LinearMCPCommands:
    """
    Linear MCP Commands

    JTBD: Как MCP команды, я хочу предоставлять интерфейс для работы с Linear,
    чтобы обеспечить интеграцию с MCP сервером.
    """

    def __init__(self):
        """Initialize Linear MCP Commands"""
        try:
            self.client = LinearAPIClient()
            self.credentials_manager = CredentialsManager()
            logger.info("Linear MCP Commands initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Linear MCP Commands: {e}")
            self.client = None
            self.credentials_manager = None

    def linear_test_connection(self) -> str:
        """
        Test Linear API connection

        Returns:
            Connection test result
        """
        if not self.client:
            return "❌ Linear API Client not initialized"

        try:
            result = self.client.test_connection()
            if result["success"]:
                return f"✅ {result['message']}"
            else:
                return f"❌ {result['message']}"
        except Exception as e:
            return f"❌ Connection test failed: {str(e)}"

    def linear_get_teams(self) -> str:
        """
        Get list of Linear teams

        Returns:
            JSON string with teams list
        """
        if not self.client:
            return "❌ Linear API Client not initialized"

        try:
            teams = self.client.get_teams()
            if teams:
                teams_info = []
                for team in teams:
                    teams_info.append(
                        {
                            "id": team.get("id"),
                            "name": team.get("name"),
                            "key": team.get("key"),
                            "description": team.get("description"),
                        }
                    )
                return f"✅ Found {len(teams)} teams: {teams_info}"
            else:
                return "❌ No teams found"
        except Exception as e:
            return f"❌ Failed to get teams: {str(e)}"

    def linear_create_issue(
        self,
        title: str,
        description: str,
        team_id: str,
        priority: int = 2,
        labels: Optional[list[str]] = None,
    ) -> str:
        """
        Create issue in Linear

        Args:
            title: Issue title
            description: Issue description
            team_id: Team ID
            priority: Priority (0-4)
            labels: List of label IDs

        Returns:
            Creation result
        """
        if not self.client:
            return "❌ Linear API Client not initialized"

        try:
            issue_id = self.client.create_issue(
                title=title,
                description=description,
                team_id=team_id,
                priority=priority,
                labels=labels,
            )

            if issue_id:
                return f"✅ Issue created successfully. ID: {issue_id}"
            else:
                return "❌ Failed to create issue"
        except Exception as e:
            return f"❌ Error creating issue: {str(e)}"

    def linear_create_cycle(
        self, name: str, start_date: str, end_date: str, team_id: str
    ) -> str:
        """
        Create cycle in Linear

        Args:
            name: Cycle name
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            team_id: Team ID

        Returns:
            Creation result
        """
        if not self.client:
            return "❌ Linear API Client not initialized"

        try:
            cycle_id = self.client.create_cycle(
                name=name, start_date=start_date, end_date=end_date, team_id=team_id
            )

            if cycle_id:
                return f"✅ Cycle created successfully. ID: {cycle_id}"
            else:
                return "❌ Failed to create cycle"
        except Exception as e:
            return f"❌ Error creating cycle: {str(e)}"

    def linear_move_issue_to_cycle(self, issue_id: str, cycle_id: str) -> str:
        """
        Move issue to cycle

        Args:
            issue_id: Issue ID
            cycle_id: Cycle ID

        Returns:
            Move result
        """
        if not self.client:
            return "❌ Linear API Client not initialized"

        try:
            success = self.client.move_issue_to_cycle(issue_id, cycle_id)

            if success:
                return f"✅ Issue {issue_id} moved to cycle {cycle_id} successfully"
            else:
                return f"❌ Failed to move issue {issue_id} to cycle {cycle_id}"
        except Exception as e:
            return f"❌ Error moving issue: {str(e)}"

    def linear_get_cycles(self, team_id: str) -> str:
        """
        Get cycles for team

        Args:
            team_id: Team ID

        Returns:
            Cycles list
        """
        if not self.client:
            return "❌ Linear API Client not initialized"

        try:
            cycles = self.client.get_cycles(team_id)
            if cycles:
                cycles_info = []
                for cycle in cycles:
                    cycles_info.append(
                        {
                            "id": cycle.get("id"),
                            "name": cycle.get("name"),
                            "start_date": cycle.get("startDate"),
                            "end_date": cycle.get("endDate"),
                            "state": cycle.get("state"),
                        }
                    )
                return f"✅ Found {len(cycles)} cycles: {cycles_info}"
            else:
                return f"❌ No cycles found for team {team_id}"
        except Exception as e:
            return f"❌ Failed to get cycles: {str(e)}"

    def linear_create_issue_from_todo(
        self, todo_file_path: str, team_id: str, priority: int = 2
    ) -> str:
        """
        Create Linear issue from todo.md file

        Args:
            todo_file_path: Path to todo.md file
            team_id: Team ID
            priority: Priority

        Returns:
            Creation result
        """
        if not self.client:
            return "❌ Linear API Client not initialized"

        try:
            # Read todo file
            with open(todo_file_path, encoding="utf-8") as f:
                content = f.read()

            # Extract title from first line
            lines = content.split("\n")
            title = lines[0].strip("# ") if lines[0].startswith("#") else "Todo Task"

            # Use first 500 chars as description
            description = content[:500] + "..." if len(content) > 500 else content

            # Create issue
            issue_id = self.client.create_issue(
                title=title, description=description, team_id=team_id, priority=priority
            )

            if issue_id:
                return f"✅ Issue created from {todo_file_path}. ID: {issue_id}"
            else:
                return f"❌ Failed to create issue from {todo_file_path}"
        except Exception as e:
            return f"❌ Error creating issue from todo: {str(e)}"

    def linear_create_cycle_from_plan(self, plan_file_path: str, team_id: str) -> str:
        """
        Create Linear cycle from release plan

        Args:
            plan_file_path: Path to plan file
            team_id: Team ID

        Returns:
            Creation result
        """
        if not self.client:
            return "❌ Linear API Client not initialized"

        try:
            # Read plan file
            with open(plan_file_path, encoding="utf-8") as f:
                content = f.read()

            # Extract cycle name from first line
            lines = content.split("\n")
            name = lines[0].strip("# ") if lines[0].startswith("#") else "Release Plan"

            # Set default dates (next 2 weeks)
            start_date = datetime.now().isoformat()[:10]
            end_date = (datetime.now() + timedelta(days=14)).isoformat()[:10]

            # Create cycle
            cycle_id = self.client.create_cycle(
                name=name, start_date=start_date, end_date=end_date, team_id=team_id
            )

            if cycle_id:
                return f"✅ Cycle created from {plan_file_path}. ID: {cycle_id}"
            else:
                return f"❌ Failed to create cycle from {plan_file_path}"
        except Exception as e:
            return f"❌ Error creating cycle from plan: {str(e)}"


# Global instance for MCP commands
linear_commands = LinearMCPCommands()
