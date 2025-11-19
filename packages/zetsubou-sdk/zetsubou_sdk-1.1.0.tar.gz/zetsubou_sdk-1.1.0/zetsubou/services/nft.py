"""
NFT Service

Handles NFT project, layer, trait, and generation management.
"""

from typing import List, Dict, Any, Optional
from ..exceptions import ZetsubouError


class NFTProject:
    """NFT Project model"""
    
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get('id')
        self.name = data.get('name')
        self.description = data.get('description')
        self.collection_config = data.get('collection_config', {})
        self.generation_config = data.get('generation_config', {})
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
        self.is_archived = data.get('is_archived', False)
        self.thumbnail_url = data.get('thumbnail_url')
        self.layers = data.get('layers', [])
        self.layer_count = data.get('layer_count', 0)
        self.generations = data.get('generations', [])
        self.generation_count = data.get('generation_count', 0)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NFTProject':
        """Create NFTProject from API response"""
        return cls(data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'collection_config': self.collection_config,
            'generation_config': self.generation_config,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_archived': self.is_archived,
            'thumbnail_url': self.thumbnail_url,
            'layers': self.layers,
            'layer_count': self.layer_count,
            'generations': self.generations,
            'generation_count': self.generation_count
        }


class NFTGeneration:
    """NFT Generation model"""
    
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get('id')
        self.project_id = data.get('project_id')
        self.total_pieces = data.get('total_pieces')
        self.status = data.get('status')
        self.created_at = data.get('created_at')
        self.started_at = data.get('started_at')
        self.completed_at = data.get('completed_at')
        self.error_message = data.get('error_message')
        self.vfs_build_folder_id = data.get('vfs_build_folder_id')
        self.vfs_images_folder_id = data.get('vfs_images_folder_id')
        self.vfs_metadata_folder_id = data.get('vfs_metadata_folder_id')
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NFTGeneration':
        """Create NFTGeneration from API response"""
        return cls(data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'total_pieces': self.total_pieces,
            'status': self.status,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'error_message': self.error_message,
            'vfs_build_folder_id': self.vfs_build_folder_id,
            'vfs_images_folder_id': self.vfs_images_folder_id,
            'vfs_metadata_folder_id': self.vfs_metadata_folder_id
        }


class NFTService:
    """Service for managing NFT projects, layers, and generations."""
    
    def __init__(self, client):
        self.client = client
    
    def list_projects(self, include_archived: bool = False) -> List[NFTProject]:
        """
        List all NFT projects.
        
        Args:
            include_archived: Whether to include archived projects
            
        Returns:
            List of NFTProject objects
        """
        params = {'include_archived': 'true' if include_archived else 'false'}
        response = self.client.get('/api/v2/nft/projects', params=params)
        data = response.json()
        if not data.get('success'):
            raise ZetsubouError(data.get('error', 'Failed to list projects'))
        return [NFTProject.from_dict(p) for p in data.get('projects', [])]
    
    def get_project(self, project_id: str) -> NFTProject:
        """
        Get details for a specific NFT project.
        
        Args:
            project_id: Project identifier
            
        Returns:
            NFTProject object
        """
        response = self.client.get(f'/api/v2/nft/projects/{project_id}')
        data = response.json()
        if not data.get('success'):
            raise ZetsubouError(data.get('error', 'Failed to get project'))
        return NFTProject.from_dict(data['project'])
    
    def create_project(
        self,
        name: str,
        collection_config: Dict[str, Any],
        description: Optional[str] = None,
        generation_config: Optional[Dict[str, Any]] = None,
        layers: Optional[List[Dict[str, Any]]] = None
    ) -> NFTProject:
        """
        Create a new NFT project.
        
        Args:
            name: Project name
            collection_config: Collection configuration (network, name, symbol, etc.)
            description: Optional project description
            generation_config: Optional generation configuration
            layers: Optional list of layers to create
            
        Returns:
            NFTProject object
        """
        payload = {
            'name': name,
            'collection_config': collection_config
        }
        if description:
            payload['description'] = description
        if generation_config:
            payload['generation_config'] = generation_config
        if layers:
            payload['layers'] = layers
        
        response = self.client.post('/api/v2/nft/projects', data=payload)
        data = response.json()
        if not data.get('success'):
            raise ZetsubouError(data.get('error', 'Failed to create project'))
        return NFTProject.from_dict(data['project'])
    
    def update_project(
        self,
        project_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        collection_config: Optional[Dict[str, Any]] = None,
        generation_config: Optional[Dict[str, Any]] = None,
        is_archived: Optional[bool] = None
    ) -> NFTProject:
        """
        Update an NFT project.
        
        Args:
            project_id: Project identifier
            name: Optional new name
            description: Optional new description
            collection_config: Optional updated collection config
            generation_config: Optional updated generation config
            is_archived: Optional archive status
            
        Returns:
            Updated NFTProject object
        """
        payload = {}
        if name is not None:
            payload['name'] = name
        if description is not None:
            payload['description'] = description
        if collection_config is not None:
            payload['collection_config'] = collection_config
        if generation_config is not None:
            payload['generation_config'] = generation_config
        if is_archived is not None:
            payload['is_archived'] = is_archived
        
        response = self.client.patch(f'/api/v2/nft/projects/{project_id}', data=payload)
        data = response.json()
        if not data.get('success'):
            raise ZetsubouError(data.get('error', 'Failed to update project'))
        return NFTProject.from_dict(data['project'])
    
    def delete_project(self, project_id: str, permanent: bool = False) -> bool:
        """
        Delete or archive an NFT project.
        
        Args:
            project_id: Project identifier
            permanent: If True, permanently delete; if False, archive
            
        Returns:
            True if successful
        """
        params = {'permanent': 'true' if permanent else 'false'}
        response = self.client._make_request('DELETE', f'/api/v2/nft/projects/{project_id}', params=params)
        data = response.json()
        if not data.get('success'):
            raise ZetsubouError(data.get('error', 'Failed to delete project'))
        return True
    
    def list_layers(self, project_id: str, include_traits: bool = True) -> List[Dict[str, Any]]:
        """
        List layers for an NFT project.
        
        Args:
            project_id: Project identifier
            include_traits: Whether to include traits in response
            
        Returns:
            List of layer dictionaries
        """
        params = {'include_traits': 'true' if include_traits else 'false'}
        response = self.client.get(f'/api/v2/nft/projects/{project_id}/layers', params=params)
        data = response.json()
        if not data.get('success'):
            raise ZetsubouError(data.get('error', 'Failed to list layers'))
        return data.get('layers', [])
    
    def create_layer(
        self,
        project_id: str,
        name: str,
        order_index: Optional[int] = None,
        is_required: bool = True,
        blend_mode: str = 'source-over',
        opacity: float = 1.0
    ) -> Dict[str, Any]:
        """
        Create a new layer in an NFT project.
        
        Args:
            project_id: Project identifier
            name: Layer name
            order_index: Optional order index (auto-assigned if not provided)
            is_required: Whether layer is required
            blend_mode: Canvas blend mode
            opacity: Layer opacity (0.0-1.0)
            
        Returns:
            Layer dictionary
        """
        payload = {
            'name': name,
            'is_required': is_required,
            'blend_mode': blend_mode,
            'opacity': opacity
        }
        if order_index is not None:
            payload['order_index'] = order_index
        
        response = self.client.post(f'/api/v2/nft/projects/{project_id}/layers', data=payload)
        data = response.json()
        if not data.get('success'):
            raise ZetsubouError(data.get('error', 'Failed to create layer'))
        return data.get('layer', {})
    
    def create_generation(
        self,
        project_id: str,
        total_pieces: int,
        config_overrides: Optional[Dict[str, Any]] = None
    ) -> NFTGeneration:
        """
        Create a new NFT generation.
        
        Args:
            project_id: Project identifier
            total_pieces: Number of NFTs to generate
            config_overrides: Optional generation config overrides
            
        Returns:
            NFTGeneration object
        """
        payload = {'total_pieces': total_pieces}
        if config_overrides:
            payload['config_overrides'] = config_overrides
        
        response = self.client.post(f'/api/v2/nft/projects/{project_id}/generate', data=payload)
        data = response.json()
        if not data.get('success'):
            raise ZetsubouError(data.get('error', 'Failed to create generation'))
        return NFTGeneration.from_dict(data['generation'])
    
    def get_generation(self, generation_id: str) -> NFTGeneration:
        """
        Get NFT generation status.
        
        Args:
            generation_id: Generation identifier
            
        Returns:
            NFTGeneration object
        """
        response = self.client.get(f'/api/v2/nft/generations/{generation_id}')
        data = response.json()
        if not data.get('success'):
            raise ZetsubouError(data.get('error', 'Failed to get generation'))
        return NFTGeneration.from_dict(data['generation'])
    
    def list_generations(self, project_id: str) -> List[NFTGeneration]:
        """
        List all generations for an NFT project.
        
        Args:
            project_id: Project identifier
            
        Returns:
            List of NFTGeneration objects
        """
        response = self.client.get(f'/api/v2/nft/projects/{project_id}/generations')
        data = response.json()
        if not data.get('success'):
            raise ZetsubouError(data.get('error', 'Failed to list generations'))
        return [NFTGeneration.from_dict(g) for g in data.get('generations', [])]
    
    def get_limits(self) -> Dict[str, Any]:
        """
        Get user's NFT tier and limits.
        
        Returns:
            Dictionary with tier, limits, and usage information
        """
        response = self.client.get('/api/v2/nft/limits')
        data = response.json()
        if not data.get('success'):
            raise ZetsubouError(data.get('error', 'Failed to get limits'))
        return {
            'tier': data.get('tier'),
            'limits': data.get('limits', {}),
            'usage': data.get('usage', {})
        }
