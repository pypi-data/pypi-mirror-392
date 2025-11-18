"""
A2A Client Implementation for Python
"""

import requests
from typing import Optional, Dict, List, Any
from urllib.parse import urlencode


class A2AClient:
    """
    A2A Client for 172.ai Platform

    This client handles all communication with the 172.ai A2A API,
    including authentication, container operations, and build management.

    Args:
        api_key (str): API key with A2A scope
        agent_id (str): Unique identifier for your agent
        agent_type (str): Agent type (code-analysis, testing, deployment, etc.)
        base_url (str, optional): Base URL for the API. Defaults to 'https://api.172.ai'
        timeout (int, optional): Request timeout in seconds. Defaults to 30

    Raises:
        ValueError: If required parameters are missing

    Example:
        >>> client = A2AClient(
        ...     api_key='sk_your_api_key',
        ...     agent_id='test-runner-v1',
        ...     agent_type='testing'
        ... )
        >>> containers = client.list_containers(limit=5)
    """

    def __init__(
        self,
        api_key: str,
        agent_id: str,
        agent_type: str,
        base_url: str = 'https://api.172.ai',
        timeout: int = 30
    ):
        if not api_key:
            raise ValueError('API key is required')
        if not agent_id:
            raise ValueError('Agent ID is required')
        if not agent_type:
            raise ValueError('Agent type is required')

        self.api_key = api_key
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

        # Base headers for all requests
        self.headers = {
            'X-API-Key': self.api_key,
            'X-Agent-Id': self.agent_id,
            'X-Agent-Type': self.agent_type,
            'Content-Type': 'application/json'
        }

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to A2A API

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data (for POST/PUT)
            params: Query parameters

        Returns:
            Response data as dictionary

        Raises:
            Exception: If request fails
        """
        url = f"{self.base_url}/v1/a2a{endpoint}"

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"A2A request failed: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = f"A2A request failed: {error_data.get('message', str(e))}"
                except:
                    pass
            raise Exception(error_msg)

    def request(self, operation: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make generic A2A request

        Args:
            operation: Operation name (e.g., 'container.list')
            params: Operation parameters

        Returns:
            Response data
        """
        return self._request('POST', '/request', {
            'operation': operation,
            'params': params or {}
        })

    # Authentication and System Methods

    def authenticate(self) -> Dict[str, Any]:
        """Authenticate with the A2A system"""
        return self._request('POST', '/authenticate')

    def get_capabilities(self) -> Dict[str, Any]:
        """Get platform capabilities"""
        return self._request('GET', '/capabilities')

    def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        return self._request('GET', '/health')

    # Container Operations

    def list_containers(
        self,
        limit: Optional[int] = None,
        scope: Optional[str] = None,
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List containers

        Args:
            limit: Maximum number of containers
            scope: Scope filter (public, private, all)
            query: Search query

        Returns:
            List of containers
        """
        params = {}
        if limit is not None:
            params['limit'] = limit
        if scope:
            params['scope'] = scope
        if query:
            params['query'] = query

        return self._request('GET', '/containers', params=params)

    def get_container(self, container_id: str) -> Dict[str, Any]:
        """
        Get container details

        Args:
            container_id: Container ID

        Returns:
            Container details
        """
        return self._request('GET', f'/containers/{container_id}')

    def create_container(self, container_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create container

        Args:
            container_data: Container parameters including:
                - name (str): Container name
                - dockerfile (str): Dockerfile content
                - tags (list, optional): Container tags
                - description (str, optional): Container description
                - isPrivate (bool, optional): Whether container is private

        Returns:
            Created container data

        Example:
            >>> container = client.create_container({
            ...     'name': f'test-env-{int(time.time())}',
            ...     'dockerfile': '''
            ...         FROM node:18-alpine
            ...         WORKDIR /app
            ...         COPY . .
            ...         RUN npm install
            ...     ''',
            ...     'tags': ['testing', 'e2e']
            ... })
        """
        request_data = {
            'operation': 'container.create',
            'params': {
                'name': container_data['name'],
                'dockerfile': container_data['dockerfile'],
                'tags': container_data.get('tags', []),
                'description': container_data.get(
                    'description',
                    f"Container created via A2A by {self.agent_id}"
                ),
                'isPrivate': container_data.get('isPrivate', True)
            }
        }

        result = self._request('POST', '/request', request_data)

        if not result.get('success'):
            raise Exception(f"Container creation failed: {result.get('message')}")

        return result['data']

    def update_container(
        self,
        container_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update container"""
        return self.request('container.update', {
            'containerId': container_id,
            **updates
        })

    def delete_container(self, container_id: str) -> Dict[str, Any]:
        """Delete container"""
        return self.request('container.delete', {'containerId': container_id})

    def build_container(self, container_id: str) -> Dict[str, Any]:
        """
        Build container

        Args:
            container_id: Container ID

        Returns:
            Build result with buildLogId

        Example:
            >>> build_result = client.build_container(container['id'])
            >>> print(f'Test build initiated: {build_result["buildLogId"]}')
        """
        result = self._request('POST', f'/containers/{container_id}/build')

        if not result.get('success'):
            raise Exception(f"Container build failed: {result.get('message')}")

        return result['data']

    # Build Operations

    def get_build_status(
        self,
        container_id: str,
        build_log_id: str
    ) -> Dict[str, Any]:
        """Get build status"""
        return self.request('build.status', {
            'containerId': container_id,
            'buildLogId': build_log_id
        })

    def get_build_logs(
        self,
        container_id: str,
        build_log_id: str
    ) -> Dict[str, Any]:
        """Get build logs"""
        return self.request('build.logs', {
            'containerId': container_id,
            'buildLogId': build_log_id
        })

    def list_builds(self, container_id: str) -> Dict[str, Any]:
        """List builds for container"""
        return self.request('build.list', {'containerId': container_id})

    # Container Execution Operations

    def start_execution(
        self,
        container_id: str,
        duration_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Start container execution

        Args:
            container_id: Container ID
            duration_days: Execution duration in days

        Returns:
            Execution details
        """
        data = {}
        if duration_days is not None:
            data['durationDays'] = duration_days

        return self._request('POST', f'/containers/{container_id}/execute', data)

    def stop_execution(self, container_id: str) -> Dict[str, Any]:
        """Stop container execution"""
        return self._request('DELETE', f'/containers/{container_id}/execute')

    def get_execution_status(self, container_id: str) -> Dict[str, Any]:
        """Get execution status"""
        return self._request('GET', f'/containers/{container_id}/execute/status')

    def get_execution_history(self, container_id: str) -> Dict[str, Any]:
        """Get execution history"""
        return self._request('GET', f'/containers/{container_id}/execute/history')

    def get_execution_cost_estimate(
        self,
        container_id: str,
        duration_days: int
    ) -> Dict[str, Any]:
        """Get cost estimate for execution"""
        return self._request(
            'GET',
            f'/executions/cost-estimate',
            params={
                'containerId': container_id,
                'durationDays': duration_days
            }
        )

    def list_executions(self) -> Dict[str, Any]:
        """List user executions"""
        return self._request('GET', '/executions')

    # File Operations

    def upload_file(
        self,
        container_id: str,
        file_path: str,
        content: str,
        mime_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Upload file to container"""
        return self.request('file.upload', {
            'containerId': container_id,
            'filePath': file_path,
            'content': content,
            'mimeType': mime_type
        })

    def list_files(
        self,
        container_id: str,
        path: str = '/'
    ) -> Dict[str, Any]:
        """List files in container"""
        return self.request('file.list', {
            'containerId': container_id,
            'path': path
        })

    def get_file(self, container_id: str, file_path: str) -> Dict[str, Any]:
        """Get file content"""
        return self.request('file.get', {
            'containerId': container_id,
            'filePath': file_path
        })

    # Container Fix Operations

    def analyze_container_failure(self, container_id: str) -> Dict[str, Any]:
        """
        Analyze container build failures with AI

        Args:
            container_id: Container ID

        Returns:
            Analysis results with fix suggestions
        """
        return self.request('container.fix.analyze', {'containerId': container_id})

    def apply_container_fix(self, container_id: str, fix_id: str) -> Dict[str, Any]:
        """
        Apply a specific AI-generated fix to a container

        Args:
            container_id: Container ID
            fix_id: Fix attempt ID

        Returns:
            Application result
        """
        return self.request('container.fix.apply', {
            'containerId': container_id,
            'fixId': fix_id
        })

    def execute_container_fix(
        self,
        container_id: str,
        auto_apply: bool = True,
        analyze_only: bool = False
    ) -> Dict[str, Any]:
        """
        Execute full fix workflow: analyze, apply fixes, and trigger rebuild

        Args:
            container_id: Container ID
            auto_apply: Auto-apply fixes (default: True)
            analyze_only: Only analyze, don't apply (default: False)

        Returns:
            Fix execution result
        """
        return self.request('container.fix.execute', {
            'containerId': container_id,
            'autoApply': auto_apply,
            'analyzeOnly': analyze_only
        })

    def get_container_fix_history(self, container_id: str) -> Dict[str, Any]:
        """
        Get history of all fix attempts for a container

        Args:
            container_id: Container ID

        Returns:
            Fix history
        """
        return self.request('container.fix.history', {'containerId': container_id})

    def get_container_fix_attempt(
        self,
        container_id: str,
        fix_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific fix attempt

        Args:
            container_id: Container ID
            fix_id: Fix attempt ID

        Returns:
            Fix attempt details
        """
        return self.request('container.fix.attempt', {
            'containerId': container_id,
            'fixId': fix_id
        })

    # Container Improvements Operations

    def suggest_container_improvements(self, container_id: str) -> Dict[str, Any]:
        """
        Get AI-powered improvement suggestions for container optimization

        Args:
            container_id: Container ID

        Returns:
            Improvement suggestions
        """
        return self.request('container.improvements.suggest', {'containerId': container_id})

    def apply_container_improvement(
        self,
        container_id: str,
        modification_id: str
    ) -> Dict[str, Any]:
        """
        Apply a specific improvement/modification to a container

        Args:
            container_id: Container ID
            modification_id: Modification ID

        Returns:
            Application result
        """
        return self.request('container.improvements.apply', {
            'containerId': container_id,
            'modificationId': modification_id
        })

    def get_improvement_status(
        self,
        container_id: str,
        modification_id: str
    ) -> Dict[str, Any]:
        """
        Get status of an applied improvement/modification

        Args:
            container_id: Container ID
            modification_id: Modification ID

        Returns:
            Improvement status
        """
        return self.request('container.improvements.status', {
            'containerId': container_id,
            'modificationId': modification_id
        })

    def list_applied_improvements(self, container_id: str) -> Dict[str, Any]:
        """
        List all applied improvements/modifications for a container

        Args:
            container_id: Container ID

        Returns:
            List of applied improvements
        """
        return self.request('container.improvements.list', {'containerId': container_id})
