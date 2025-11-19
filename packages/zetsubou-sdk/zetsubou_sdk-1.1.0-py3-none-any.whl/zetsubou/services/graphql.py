"""
GraphQL Service

Handles GraphQL queries and mutations.
"""

from typing import Dict, Any, Optional
from ..exceptions import ZetsubouError


class GraphQLService:
    """Service for executing GraphQL queries and mutations."""
    
    def __init__(self, client):
        self.client = client
    
    def query(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a GraphQL query.
        
        Args:
            query: GraphQL query string
            variables: Optional query variables
            operation_name: Optional operation name for multi-operation queries
            
        Returns:
            Dictionary with 'data' and optionally 'errors' keys
            
        Example:
            >>> result = client.graphql.query(
            ...     query='{ viewer { username tier } }'
            ... )
            >>> print(result['data']['viewer']['username'])
        """
        payload = {'query': query}
        if variables:
            payload['variables'] = variables
        if operation_name:
            payload['operationName'] = operation_name
        
        response = self.client.post('/api/graphql', data=payload)
        data = response.json()
        
        # Check for GraphQL errors
        if 'errors' in data and data['errors']:
            error_messages = [e.get('message', 'Unknown error') for e in data['errors']]
            raise ZetsubouError(f"GraphQL errors: {'; '.join(error_messages)}")
        
        return data
    
    def mutate(
        self,
        mutation: str,
        variables: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a GraphQL mutation.
        
        Args:
            mutation: GraphQL mutation string
            variables: Optional mutation variables
            operation_name: Optional operation name
            
        Returns:
            Dictionary with 'data' and optionally 'errors' keys
            
        Example:
            >>> result = client.graphql.mutate(
            ...     mutation='''
            ...     mutation {
            ...       createNftProject(
            ...         name: "My Project"
            ...         collectionConfig: {...}
            ...       ) {
            ...         success
            ...         project { id name }
            ...       }
            ...     }
            ...     '''
            ... )
        """
        return self.query(mutation, variables, operation_name)
    
    def health_check(self) -> str:
        """
        Simple GraphQL health check.
        
        Returns:
            "ok" if the GraphQL endpoint is accessible
        """
        result = self.query('{ health }')
        return result.get('data', {}).get('health', 'unknown')

