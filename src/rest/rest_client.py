"""REST API client for Rick and Morty API."""
import requests
from typing import List, Dict, Any, Optional, Tuple
import logging
from urllib.parse import urljoin, urlparse, parse_qs

from ..shared.config import Config
from ..shared.models import Character, Location, PaginationInfo, APIResponse
from ..shared.utils import (
    setup_logging, retry_with_backoff, validate_response, 
    handle_api_error, APIError, ProgressTracker
)

logger = setup_logging(__name__)

class RESTClient:
    """REST API client for Rick and Morty API."""
    
    def __init__(self, base_url: str = Config.REST_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'RickAndMortyClient/1.0'
        })
    
    @retry_with_backoff()
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make HTTP request to API."""
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
            raise APIError(f"Request failed: {str(e)}")
    
    def _parse_pagination_info(self, info: Dict[str, Any]) -> PaginationInfo:
        """Parse pagination information from API response."""
        return PaginationInfo(
            count=info.get('count', 0),
            pages=info.get('pages', 0),
            next=info.get('next'),
            prev=info.get('prev')
        )
    
    def _get_page_number_from_url(self, url: Optional[str]) -> Optional[int]:
        """Extract page number from URL."""
        if not url:
            return None
        
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        page = params.get('page', [None])[0]
        
        return int(page) if page else None
    
    def fetch_characters_page(self, page: int = 1) -> Tuple[List[Character], PaginationInfo]:
        """Fetch a single page of characters."""
        logger.info(f"Fetching characters page {page}")
        
        data = self._make_request('/character', params={'page': page})
        
        info = self._parse_pagination_info(data.get('info', {}))
        results = data.get('results', [])
        
        characters = [Character.from_dict(char_data) for char_data in results]
        
        return characters, info
    
    def fetch_all_characters(self) -> List[Character]:
        """Fetch all characters with pagination."""
        all_characters = []
        page = 1
        
        # First request to get total pages
        characters, info = self.fetch_characters_page(page)
        all_characters.extend(characters)
        
        total_pages = info.pages
        logger.info(f"Total character pages to fetch: {total_pages}")
        
        # Set up progress tracking
        progress = ProgressTracker(total_pages, "Fetching characters")
        progress.update(1)
        
        # Fetch remaining pages
        while page < total_pages:
            page += 1
            characters, _ = self.fetch_characters_page(page)
            all_characters.extend(characters)
            progress.update(1)
        
        progress.finish()
        logger.info(f"Fetched {len(all_characters)} characters total")
        
        return all_characters
    
    def fetch_locations_page(self, page: int = 1) -> Tuple[List[Location], PaginationInfo]:
        """Fetch a single page of locations."""
        logger.info(f"Fetching locations page {page}")
        
        data = self._make_request('/location', params={'page': page})
        
        info = self._parse_pagination_info(data.get('info', {}))
        results = data.get('results', [])
        
        locations = [Location.from_dict(loc_data) for loc_data in results]
        
        return locations, info
    
    def fetch_all_locations(self) -> List[Location]:
        """Fetch all locations with pagination."""
        all_locations = []
        page = 1
        
        # First request to get total pages
        locations, info = self.fetch_locations_page(page)
        all_locations.extend(locations)
        
        total_pages = info.pages
        logger.info(f"Total location pages to fetch: {total_pages}")
        
        # Set up progress tracking
        progress = ProgressTracker(total_pages, "Fetching locations")
        progress.update(1)
        
        # Fetch remaining pages
        while page < total_pages:
            page += 1
            locations, _ = self.fetch_locations_page(page)
            all_locations.extend(locations)
            progress.update(1)
        
        progress.finish()
        logger.info(f"Fetched {len(all_locations)} locations total")
        
        return all_locations
    
    def fetch_character_by_id(self, character_id: int) -> Character:
        """Fetch a single character by ID."""
        data = self._make_request(f'/character/{character_id}')
        return Character.from_dict(data)
    
    def fetch_location_by_id(self, location_id: int) -> Location:
        """Fetch a single location by ID."""
        data = self._make_request(f'/location/{location_id}')
        return Location.from_dict(data)
    
    def fetch_character_with_location(self, character_id: int) -> Dict[str, Any]:
        """Fetch character with full location details."""
        character = self.fetch_character_by_id(character_id)
        
        location_id = character.get_location_id()
        location = None
        
        if location_id:
            try:
                location = self.fetch_location_by_id(location_id)
            except APIError as e:
                logger.warning(f"Failed to fetch location {location_id}: {str(e)}")
        
        return {
            'character': character,
            'location': location
        }
    
    def close(self):
        """Close the session."""
        self.session.close()