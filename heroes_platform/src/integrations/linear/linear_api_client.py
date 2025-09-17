"""
Linear API Client
JTBD: Как API клиент, я хочу взаимодействовать с Linear GraphQL API,
чтобы обеспечить создание и управление задачами, циклами и командами.

Поддерживает:
- Создание задач (issues)
- Создание циклов (cycles)
- Управление командами (teams)
- Перемещение задач между циклами
"""

import os
import sys
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Import credentials manager
from heroes_platform.shared.credentials_manager import CredentialsManager

logger = logging.getLogger(__name__)


class LinearAPIClient:
    """
    Linear GraphQL API Client
    
    JTBD: Как API клиент, я хочу управлять взаимодействием с Linear,
    чтобы обеспечить автоматическое создание и управление задачами.
    """

    def __init__(self):
        """
        JTBD: Как инициализатор, я хочу настроить GraphQL клиент,
        чтобы обеспечить готовность к работе с Linear API.
        """
        self.api_key = self._get_api_key()
        if not self.api_key:
            raise ValueError("Linear API key not found")
        
        # Setup GraphQL transport
        transport = RequestsHTTPTransport(
            url='https://api.linear.app/graphql',
            headers={
                'Authorization': self.api_key,
                'Content-Type': 'application/json',
            }
        )
        
        self.client = Client(transport=transport, fetch_schema_from_transport=True)
        logger.info("Linear API Client initialized successfully")

    def _get_api_key(self) -> Optional[str]:
        """
        JTBD: Как менеджер секретов, я хочу получать API ключ,
        чтобы обеспечить аутентификацию с Linear.
        """
        try:
            cm = CredentialsManager()
            result = cm.get_credential("linear_api_key")
            if result.success and result.value:
                return result.value
            else:
                logger.error(f"Failed to get Linear API key: {result.error}")
                return None
        except Exception as e:
            logger.error(f"Error getting Linear API key: {e}")
            return None

    def get_teams(self) -> List[Dict[str, Any]]:
        """
        JTBD: Как менеджер команд, я хочу получать список команд,
        чтобы обеспечить правильное назначение задач.
        """
        query = gql("""
            query GetTeams {
                teams {
                    nodes {
                        id
                        name
                        key
                        description
                    }
                }
            }
        """)
        
        try:
            result = self.client.execute(query)
            teams = result.get('teams', {}).get('nodes', [])
            logger.info(f"Retrieved {len(teams)} teams from Linear")
            return teams
        except Exception as e:
            logger.error(f"Error getting teams: {e}")
            return []

    def create_issue(self, title: str, description: str, team_id: str, 
                    priority: int = 2, labels: Optional[List[str]] = None) -> Optional[str]:
        """
        JTBD: Как создатель задач, я хочу создавать задачи в Linear,
        чтобы обеспечить отслеживание работы.
        
        Args:
            title: Заголовок задачи
            description: Описание задачи
            team_id: ID команды
            priority: Приоритет (0-4, где 0 - No priority, 4 - Urgent)
            labels: Список меток
            
        Returns:
            ID созданной задачи или None при ошибке
        """
        mutation = gql("""
            mutation CreateIssue($input: IssueCreateInput!) {
                issueCreate(input: $input) {
                    success
                    issue {
                        id
                        title
                        url
                    }
                }
            }
        """)
        
        variables = {
            "input": {
                "title": title,
                "description": description,
                "teamId": team_id,
                "priority": priority
            }
        }
        
        if labels:
            variables["input"]["labelIds"] = labels
        
        try:
            result = self.client.execute(mutation, variable_values=variables)
            issue_create = result.get('issueCreate', {})
            
            if issue_create.get('success'):
                issue = issue_create.get('issue', {})
                issue_id = issue.get('id')
                logger.info(f"Created issue: {issue.get('title')} (ID: {issue_id})")
                return issue_id
            else:
                logger.error("Failed to create issue")
                return None
                
        except Exception as e:
            logger.error(f"Error creating issue: {e}")
            return None

    def create_cycle(self, name: str, start_date: str, end_date: str, 
                    team_id: str) -> Optional[str]:
        """
        JTBD: Как менеджер релизов, я хочу создавать циклы в Linear,
        чтобы обеспечить планирование релизов.
        
        Args:
            name: Название цикла
            start_date: Дата начала (ISO format)
            end_date: Дата окончания (ISO format)
            team_id: ID команды
            
        Returns:
            ID созданного цикла или None при ошибке
        """
        mutation = gql("""
            mutation CreateCycle($input: CycleCreateInput!) {
                cycleCreate(input: $input) {
                    success
                    cycle {
                        id
                        name
                        startDate
                        endDate
                    }
                }
            }
        """)
        
        variables = {
            "input": {
                "name": name,
                "teamId": team_id,
                "startDate": start_date,
                "endDate": end_date
            }
        }
        
        try:
            result = self.client.execute(mutation, variable_values=variables)
            cycle_create = result.get('cycleCreate', {})
            
            if cycle_create.get('success'):
                cycle = cycle_create.get('cycle', {})
                cycle_id = cycle.get('id')
                logger.info(f"Created cycle: {cycle.get('name')} (ID: {cycle_id})")
                return cycle_id
            else:
                logger.error("Failed to create cycle")
                return None
                
        except Exception as e:
            logger.error(f"Error creating cycle: {e}")
            return None

    def move_issue_to_cycle(self, issue_id: str, cycle_id: str) -> bool:
        """
        JTBD: Как менеджер задач, я хочу перемещать задачи в циклы,
        чтобы обеспечить планирование работы.
        
        Args:
            issue_id: ID задачи
            cycle_id: ID цикла
            
        Returns:
            True при успехе, False при ошибке
        """
        mutation = gql("""
            mutation UpdateIssue($id: String!, $input: IssueUpdateInput!) {
                issueUpdate(id: $id, input: $input) {
                    success
                    issue {
                        id
                        title
                        cycle {
                            id
                            name
                        }
                    }
                }
            }
        """)
        
        variables = {
            "id": issue_id,
            "input": {
                "cycleId": cycle_id
            }
        }
        
        try:
            result = self.client.execute(mutation, variable_values=variables)
            issue_update = result.get('issueUpdate', {})
            
            if issue_update.get('success'):
                issue = issue_update.get('issue', {})
                cycle = issue.get('cycle', {})
                logger.info(f"Moved issue {issue.get('title')} to cycle {cycle.get('name')}")
                return True
            else:
                logger.error("Failed to move issue")
                return False
                
        except Exception as e:
            logger.error(f"Error moving issue: {e}")
            return False

    def get_cycles(self, team_id: str) -> List[Dict[str, Any]]:
        """
        JTBD: Как менеджер циклов, я хочу получать список циклов команды,
        чтобы обеспечить правильное планирование.
        
        Args:
            team_id: ID команды
            
        Returns:
            Список циклов
        """
        query = gql("""
            query GetCycles($teamId: String!) {
                cycles(filter: { team: { id: { eq: $teamId } } }) {
                    nodes {
                        id
                        name
                        startDate
                        endDate
                        state
                    }
                }
            }
        """)
        
        try:
            result = self.client.execute(query, variable_values={"teamId": team_id})
            cycles = result.get('cycles', {}).get('nodes', [])
            logger.info(f"Retrieved {len(cycles)} cycles for team {team_id}")
            return cycles
        except Exception as e:
            logger.error(f"Error getting cycles: {e}")
            return []

    def test_connection(self) -> Dict[str, Any]:
        """
        JTBD: Как тестер, я хочу проверять подключение к Linear API,
        чтобы обеспечить диагностику проблем.
        
        Returns:
            Результат тестирования
        """
        try:
            teams = self.get_teams()
            return {
                "success": True,
                "teams_count": len(teams),
                "api_key_valid": True,
                "message": f"Linear API connected successfully. Found {len(teams)} teams."
            }
        except Exception as e:
            return {
                "success": False,
                "teams_count": 0,
                "api_key_valid": False,
                "message": f"Linear API connection failed: {str(e)}"
            }
