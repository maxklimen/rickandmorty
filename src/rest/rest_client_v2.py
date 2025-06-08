"""Refactored REST API client for Rick and Morty API."""
import requests
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin

from ..shared.base_client import BaseAPIClient, APIImplementationType
from ..shared.config import Config
from ..shared.models import Character, Location
from ..shared.utils import (
    setup_logging, retry_with_backoff, validate_response, 
    handle_api_error, APIError
)

class RESTClient(BaseAPIClient):
    """REST API client implementation for Rick and Morty API.
    
    This client uses traditional REST API calls with pagination to fetch data.
    It inherits common functionality from BaseAPIClient and implements the
    REST-specific fetching logic.
    """
    
    def __init__(self, base_url: str = Config.REST_BASE_URL):
        """Initialize the REST client.
        
        Args:
            base_url: Base URL for the REST API
        """
        super().__init__(APIImplementationType.REST)
        
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'RickAndMortyRESTClient/2.0'
        })
        
        self.logger.info(f"Initialized REST client with base URL: {base_url}")
    
    def fetch_all_characters(self) -> List[Character]:
        """Fetch all characters using REST API with pagination.
        
        Returns:
            List of all Character objects
            
        Raises:
            APIError: If the fetch operation fails
        """
        def fetch_page(page: int) -> Dict[str, Any]:
            return self._make_request('character', {'page': page})
        
        def parse_character(data: Dict[str, Any]) -> Character:
            return Character.from_dict(data)
        
        return self._paginate_with_progress(
            fetch_page, 
            "characters", 
            parse_character
        )
    
    def fetch_all_locations(self) -> List[Location]:
        """Fetch all locations using REST API with pagination.
        
        Returns:
            List of all Location objects
            
        Raises:
            APIError: If the fetch operation fails
        """
        def fetch_page(page: int) -> Dict[str, Any]:
            return self._make_request('location', {'page': page})
        
        def parse_location(data: Dict[str, Any]) -> Location:
            return Location.from_dict(data)
        
        return self._paginate_with_progress(
            fetch_page,
            "locations",
            parse_location
        )
    
    def fetch_character_with_location(self, character_id: int) -> Dict[str, Any]:
        """Fetch a specific character with detailed location information.
        
        Args:
            character_id: The ID of the character to fetch
            
        Returns:
            Dictionary containing 'character' and 'location' keys
            
        Raises:
            APIError: If the fetch operation fails
        """
        self.logger.info(f"Fetching character {character_id} with location details")
        
        try:
            # Fetch character data
            char_data = self._make_request(f'character/{character_id}')
            character = Character.from_dict(char_data)
            
            # Fetch location data if character has a location
            location = None
            location_id = character.get_location_id()
            if location_id:
                try:
                    loc_data = self._make_request(f'location/{location_id}')
                    location = Location.from_dict(loc_data)
                except APIError as e:
                    self.logger.warning(f"Could not fetch location {location_id}: {e}")
            
            return {
                'character': character,
                'location': location
            }
            
        except APIError as e:
            if hasattr(e, 'status_code') and e.status_code == 404:
                raise APIError(f"Character {character_id} not found", status_code=404)
            raise
    
    def close(self) -> None:
        """Clean up any resources used by the client."""
        if self.session:
            self.session.close()
            self.logger.info("REST client session closed")
    
    # REST-specific implementation details
    
    @retry_with_backoff()
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make HTTP request to REST API.
        
        Args:
            endpoint: API endpoint to call
            params: Optional query parameters
            
        Returns:
            JSON response data
            
        Raises:
            APIError: If the request fails
        """
        # Fix URL construction - ensure trailing slash for proper urljoin behavior
        base_url = self.base_url.rstrip('/') + '/'
        endpoint = endpoint.lstrip('/')
        url = urljoin(base_url, endpoint)
        
        try:
            response = self.session.get(url, params=params, timeout=Config.TIMEOUT)
            
            if response.status_code != 200:
                handle_api_error(response)
            
            if not validate_response(response):
                raise APIError("Invalid response format")
            
            return response.json()
            
        except requests.exceptions.Timeout:
            raise APIError("Request timeout", status_code=408)
        except requests.exceptions.ConnectionError:
            raise APIError("Connection error")
        except requests.exceptions.RequestException as e:
            raise APIError(f"HTTP request failed: {str(e)}")
    
    # Override base class methods to provide REST-specific information
    
    def _supports_batch_queries(self) -> bool:
        """REST doesn't support batch queries in a single request."""
        return False
    
    def _supports_relationship_optimization(self) -> bool:
        """REST requires separate calls for related data."""
        return False
    
    def _estimate_api_calls(self) -> int:
        """Estimate API calls needed for full dataset."""
        # 42 character pages + 7 location pages
        return 49
    
    def _get_performance_characteristics(self) -> Dict[str, str]:
        """Describe REST performance characteristics."""
        return {
            'latency': 'Low per request',
            'throughput': 'High',
            'optimization_level': 'Standard pagination',
            'caching': 'HTTP-level caching supported',
            'complexity': 'Simple, predictable'
        }
    
    def get_client_specific_info(self) -> Dict[str, Any]:
        """Get REST-specific client information."""
        return {
            'base_url': self.base_url,
            'session_headers': dict(self.session.headers),
            'timeout': Config.TIMEOUT,
            'pagination_method': 'URL-based pagination',
            'authentication': 'None required',
            'rate_limiting': 'Handled with exponential backoff'
        }