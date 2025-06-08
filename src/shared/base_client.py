"""Abstract base client for Rick and Morty API implementations."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable
import logging
from enum import Enum

from .models import Character, Location
from .utils import setup_logging, ProgressTracker, APIError

logger = setup_logging(__name__)

class APIImplementationType(Enum):
    """Supported API implementation types."""
    REST = "REST"
    GRAPHQL = "GraphQL"

class BaseAPIClient(ABC):
    """Abstract base class for all Rick and Morty API client implementations.
    
    This class defines the common interface and shared functionality that all
    API implementations (REST, GraphQL, etc.) must provide.
    """
    
    def __init__(self, implementation_type: APIImplementationType):
        """Initialize the base client.
        
        Args:
            implementation_type: The type of API implementation
        """
        self.implementation_type = implementation_type
        self.logger = setup_logging(f"{__name__}.{implementation_type.value}")
        
    # Abstract methods that must be implemented by subclasses
    
    @abstractmethod
    def fetch_all_characters(self) -> List[Character]:
        """Fetch all characters from the API.
        
        Returns:
            List of all Character objects
            
        Raises:
            APIError: If the fetch operation fails
        """
        pass
    
    @abstractmethod
    def fetch_all_locations(self) -> List[Location]:
        """Fetch all locations from the API.
        
        Returns:
            List of all Location objects
            
        Raises:
            APIError: If the fetch operation fails
        """
        pass
    
    @abstractmethod
    def fetch_character_with_location(self, character_id: int) -> Dict[str, Any]:
        """Fetch a specific character with detailed location information.
        
        Args:
            character_id: The ID of the character to fetch
            
        Returns:
            Dictionary containing 'character' and 'location' keys
            
        Raises:
            APIError: If the fetch operation fails
        """
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Clean up any resources used by the client."""
        pass
    
    # Shared utility methods available to all implementations
    
    def _paginate_with_progress(
        self, 
        fetch_func: Callable[[int], Dict[str, Any]], 
        description: str,
        parser_func: Callable[[Dict[str, Any]], Any]
    ) -> List[Any]:
        """Common pagination logic with progress tracking.
        
        Args:
            fetch_func: Function that takes page number and returns API response
            description: Description for progress tracking
            parser_func: Function to parse individual items from response
            
        Returns:
            List of parsed items
        """
        self.logger.info(f"Starting paginated fetch: {description}")
        
        all_items = []
        page = 1
        
        # First request to get pagination info
        first_response = fetch_func(page)
        info = first_response.get('info', {})
        total_pages = info.get('pages', 1)
        
        self.logger.info(f"Total pages to fetch: {total_pages}")
        
        # Process first page
        results = first_response.get('results', [])
        for item_data in results:
            item = parser_func(item_data)
            all_items.append(item)
        
        # Set up progress tracking for remaining pages
        if total_pages > 1:
            progress = ProgressTracker(total_pages - 1, f"Fetching {description}")
            
            for page in range(2, total_pages + 1):
                try:
                    response = fetch_func(page)
                    results = response.get('results', [])
                    
                    for item_data in results:
                        item = parser_func(item_data)
                        all_items.append(item)
                    
                    progress.update(1)
                    
                except Exception as e:
                    self.logger.error(f"Error fetching page {page}: {e}")
                    progress.finish()
                    raise APIError(f"Failed to fetch {description} page {page}: {e}")
            
            progress.finish()
        
        self.logger.info(f"Fetched {len(all_items)} {description} total")
        return all_items
    
    def get_implementation_info(self) -> Dict[str, Any]:
        """Get information about this API implementation.
        
        Returns:
            Dictionary with implementation details
        """
        return {
            'type': self.implementation_type.value,
            'class': self.__class__.__name__,
            'supports_batch_queries': self._supports_batch_queries(),
            'supports_relationship_optimization': self._supports_relationship_optimization(),
            'estimated_api_calls_for_full_dataset': self._estimate_api_calls(),
            'performance_characteristics': self._get_performance_characteristics()
        }
    
    # Methods that can be overridden by implementations for specific behavior
    
    def _supports_batch_queries(self) -> bool:
        """Override to indicate if implementation supports batch queries."""
        return False
    
    def _supports_relationship_optimization(self) -> bool:
        """Override to indicate if implementation can optimize relationship queries."""
        return False
    
    def _estimate_api_calls(self) -> int:
        """Override to provide estimate of API calls needed for full dataset."""
        return 49  # Default: 42 character pages + 7 location pages
    
    def _get_performance_characteristics(self) -> Dict[str, str]:
        """Override to describe performance characteristics."""
        return {
            'latency': 'Unknown',
            'throughput': 'Unknown',
            'optimization_level': 'Standard'
        }
    
    def __str__(self) -> str:
        """String representation of the client."""
        return f"{self.implementation_type.value}APIClient"
    
    def __repr__(self) -> str:
        """Detailed string representation of the client."""
        return f"{self.__class__.__name__}(type={self.implementation_type.value})"