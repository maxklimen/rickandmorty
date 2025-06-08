"""Refactored GraphQL API client for Rick and Morty API."""
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from typing import List, Dict, Any, Optional
import time

from ..shared.base_client import BaseAPIClient, APIImplementationType
from ..shared.config import Config
from ..shared.models import Character, Location
from ..shared.utils import setup_logging, APIError, extract_id_from_url

class GraphQLClient(BaseAPIClient):
    """GraphQL API client implementation for Rick and Morty API.
    
    This client uses GraphQL queries to fetch data with support for optimization
    strategies including combined queries and relationship fetching.
    """
    
    # GraphQL query definitions
    CHARACTERS_QUERY = gql("""
        query GetCharacters($page: Int!) {
            characters(page: $page) {
                info {
                    count
                    pages
                    next
                    prev
                }
                results {
                    id
                    name
                    status
                    species
                    type
                    gender
                    origin {
                        name
                    }
                    location {
                        id
                        name
                    }
                    image
                    episode {
                        id
                    }
                    created
                }
            }
        }
    """)
    
    LOCATIONS_QUERY = gql("""
        query GetLocations($page: Int!) {
            locations(page: $page) {
                info {
                    count
                    pages
                    next
                    prev
                }
                results {
                    id
                    name
                    type
                    dimension
                    residents {
                        id
                    }
                    created
                }
            }
        }
    """)
    
    CHARACTER_BY_ID_QUERY = gql("""
        query GetCharacter($id: ID!) {
            character(id: $id) {
                id
                name
                status
                species
                type
                gender
                origin {
                    name
                }
                location {
                    id
                    name
                }
                image
                episode {
                    id
                }
                created
            }
        }
    """)
    
    LOCATION_BY_ID_QUERY = gql("""
        query GetLocation($id: ID!) {
            location(id: $id) {
                id
                name
                type
                dimension
                residents {
                    id
                }
                created
            }
        }
    """)
    
    # Optimization queries
    ALL_DATA_QUERY = gql("""
        query GetAllData {
            characters {
                info {
                    count
                    pages
                }
                results {
                    id
                    name
                    status
                    species
                    origin {
                        name
                    }
                    location {
                        id
                        name
                    }
                }
            }
            locations {
                info {
                    count
                    pages
                }
                results {
                    id
                    name
                    type
                    dimension
                    residents {
                        id
                    }
                }
            }
        }
    """)
    
    COMBINED_PAGE_QUERY = gql("""
        query GetCombinedPage($charPage: Int!, $locPage: Int!) {
            characters(page: $charPage) {
                info { count pages next prev }
                results {
                    id name status species type gender image created
                    origin { name }
                    location { id name }
                    episode { id }
                }
            }
            locations(page: $locPage) {
                info { count pages next prev }
                results {
                    id name type dimension created
                    residents { id }
                }
            }
        }
    """)
    
    def __init__(self, url: str = Config.GRAPHQL_URL):
        """Initialize the GraphQL client.
        
        Args:
            url: GraphQL endpoint URL
        """
        super().__init__(APIImplementationType.GRAPHQL)
        
        self.url = url
        transport = RequestsHTTPTransport(
            url=url,
            headers={'User-Agent': 'RickAndMortyGraphQLClient/2.0'},
            timeout=Config.TIMEOUT
        )
        self.client = Client(transport=transport, fetch_schema_from_transport=True)
        
        self.logger.info(f"Initialized GraphQL client with URL: {url}")
    
    def fetch_all_characters(self) -> List[Character]:
        """Fetch all characters using GraphQL with pagination.
        
        Returns:
            List of all Character objects
            
        Raises:
            APIError: If the fetch operation fails
        """
        def fetch_page(page: int) -> Dict[str, Any]:
            return self._execute_query(self.CHARACTERS_QUERY, {'page': page})
        
        def parse_character(data: Dict[str, Any]) -> Character:
            return self._parse_character(data)
        
        characters = self._paginate_with_progress(
            fetch_page,
            "characters",
            parse_character
        )
        
        self.logger.info(f"Fetched {len(characters)} characters via GraphQL")
        return characters
    
    def fetch_all_locations(self) -> List[Location]:
        """Fetch all locations using GraphQL with pagination.
        
        Returns:
            List of all Location objects
            
        Raises:
            APIError: If the fetch operation fails
        """
        def fetch_page(page: int) -> Dict[str, Any]:
            return self._execute_query(self.LOCATIONS_QUERY, {'page': page})
        
        def parse_location(data: Dict[str, Any]) -> Location:
            return self._parse_location(data)
        
        locations = self._paginate_with_progress(
            fetch_page,
            "locations",
            parse_location
        )
        
        self.logger.info(f"Fetched {len(locations)} locations via GraphQL")
        return locations
    
    def fetch_character_with_location(self, character_id: int) -> Dict[str, Any]:
        """Fetch a specific character with detailed location information.
        
        Args:
            character_id: The ID of the character to fetch
            
        Returns:
            Dictionary containing 'character' and 'location' keys
            
        Raises:
            APIError: If the fetch operation fails
        """
        self.logger.info(f"Fetching character {character_id} with location details via GraphQL")
        
        try:
            # Fetch character data
            char_result = self._execute_query(self.CHARACTER_BY_ID_QUERY, {'id': str(character_id)})
            char_data = char_result.get('character')
            
            if not char_data:
                raise APIError(f"Character {character_id} not found", status_code=404)
            
            character = self._parse_character(char_data)
            
            # Fetch location data if character has a location
            location = None
            location_id = character.get_location_id()
            if location_id:
                try:
                    loc_result = self._execute_query(self.LOCATION_BY_ID_QUERY, {'id': str(location_id)})
                    loc_data = loc_result.get('location')
                    if loc_data:
                        location = self._parse_location(loc_data)
                except APIError as e:
                    self.logger.warning(f"Could not fetch location {location_id}: {e}")
            
            return {
                'character': character,
                'location': location
            }
            
        except Exception as e:
            if "not found" in str(e).lower():
                raise APIError(f"Character {character_id} not found", status_code=404)
            raise APIError(f"Failed to fetch character {character_id}: {str(e)}")
    
    def close(self) -> None:
        """Clean up any resources used by the client."""
        # GraphQL client doesn't require explicit cleanup
        self.logger.info("GraphQL client closed")
    
    # GraphQL optimization methods
    
    def fetch_all_data_optimized(self) -> Dict[str, List[Any]]:
        """Fetch first page of all data in a single optimized query."""
        self.logger.info("Fetching data using optimized GraphQL query")
        
        result = self._execute_query(self.ALL_DATA_QUERY)
        
        characters = []
        for char_data in result.get('characters', {}).get('results', []):
            character = self._parse_character(char_data)
            characters.append(character)
        
        locations = []
        for loc_data in result.get('locations', {}).get('results', []):
            location = self._parse_location(loc_data)
            locations.append(location)
        
        self.logger.info(f"Fetched {len(characters)} characters and {len(locations)} locations in single query")
        
        return {
            'characters': characters,
            'locations': locations
        }
    
    def fetch_all_data_ultra_optimized(self) -> Dict[str, Any]:
        """Fetch ALL data using optimized combined queries - reduces API calls significantly."""
        start_time = time.time()
        
        self.logger.info("Starting ultra-optimized GraphQL data fetch...")
        
        # First, get pagination info from the simple query
        first_result = self._execute_query(self.ALL_DATA_QUERY)
        char_pages = first_result.get('characters', {}).get('info', {}).get('pages', 42)
        loc_pages = first_result.get('locations', {}).get('info', {}).get('pages', 7)
        
        self.logger.info(f"Detected {char_pages} character pages and {loc_pages} location pages")
        
        all_characters = []
        all_locations = []
        
        # Add first page data we already have
        for char_data in first_result.get('characters', {}).get('results', []):
            character = self._parse_character(char_data)
            all_characters.append(character)
        
        for loc_data in first_result.get('locations', {}).get('results', []):
            location = self._parse_location(loc_data)
            all_locations.append(location)
        
        # Fetch remaining pages using combined queries
        remaining_char_pages = list(range(2, char_pages + 1))
        remaining_loc_pages = list(range(2, loc_pages + 1))
        
        queries_made = 1  # First query already made
        
        # Smart optimization: Combine character and location fetching
        i = 0
        while i < len(remaining_char_pages) or i < len(remaining_loc_pages):
            char_page = remaining_char_pages[i] if i < len(remaining_char_pages) else None
            loc_page = remaining_loc_pages[i] if i < len(remaining_loc_pages) else None
            
            if char_page and loc_page:
                # Both available - use combined query
                variables = {'charPage': char_page, 'locPage': loc_page}
                try:
                    result = self._execute_query(self.COMBINED_PAGE_QUERY, variables)
                    queries_made += 1
                    
                    # Process both character and location results
                    char_results = result.get('characters', {}).get('results', [])
                    for char_data in char_results:
                        character = self._parse_character(char_data)
                        all_characters.append(character)
                    
                    loc_results = result.get('locations', {}).get('results', [])
                    for loc_data in loc_results:
                        location = self._parse_location(loc_data)
                        all_locations.append(location)
                        
                except Exception as e:
                    self.logger.error(f"Error fetching combined page char={char_page}, loc={loc_page}: {e}")
                    # Fallback to individual queries
                    if char_page:
                        char_result = self._execute_query(self.CHARACTERS_QUERY, {'page': char_page})
                        queries_made += 1
                        for char_data in char_result.get('characters', {}).get('results', []):
                            character = self._parse_character(char_data)
                            all_characters.append(character)
                    
                    if loc_page:
                        loc_result = self._execute_query(self.LOCATIONS_QUERY, {'page': loc_page})
                        queries_made += 1
                        for loc_data in loc_result.get('locations', {}).get('results', []):
                            location = self._parse_location(loc_data)
                            all_locations.append(location)
            
            elif char_page:
                # Only character page remaining
                try:
                    char_result = self._execute_query(self.CHARACTERS_QUERY, {'page': char_page})
                    queries_made += 1
                    for char_data in char_result.get('characters', {}).get('results', []):
                        character = self._parse_character(char_data)
                        all_characters.append(character)
                except Exception as e:
                    self.logger.error(f"Error fetching character page {char_page}: {e}")
            
            i += 1
        
        total_time = time.time() - start_time
        
        self.logger.info(f"Ultra-optimized fetch completed!")
        self.logger.info(f"  Total API calls: {queries_made} (vs 49 in original)")
        self.logger.info(f"  API call reduction: {((49 - queries_made) / 49 * 100):.1f}%")
        self.logger.info(f"  Total time: {total_time:.2f}s")
        self.logger.info(f"  Characters fetched: {len(all_characters)}")
        self.logger.info(f"  Locations fetched: {len(all_locations)}")
        
        return {
            'characters': all_characters,
            'locations': all_locations,
            'api_calls': queries_made,
            'total_time': total_time,
            'optimization_percentage': ((49 - queries_made) / 49 * 100)
        }
    
    # GraphQL-specific implementation details
    
    def _execute_query(self, query, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a GraphQL query.
        
        Args:
            query: GQL query object
            variables: Optional query variables
            
        Returns:
            Query result data
            
        Raises:
            APIError: If the query fails
        """
        try:
            result = self.client.execute(query, variable_values=variables)
            return result
        except Exception as e:
            raise APIError(f"GraphQL query failed: {str(e)}")
    
    def _parse_character(self, data: Dict[str, Any]) -> Character:
        """Parse character data from GraphQL response."""
        # Handle nested location data
        location_data = data.get('location', {})
        if location_data and location_data.get('id'):
            # Construct URL format for compatibility
            location_data['url'] = f"{Config.REST_BASE_URL}/location/{location_data['id']}"
        
        # Convert episode list to URL format for compatibility
        episodes = data.get('episode', [])
        episode_urls = [f"{Config.REST_BASE_URL}/episode/{ep['id']}" for ep in episodes]
        
        char_dict = {
            'id': int(data['id']),
            'name': data['name'],
            'status': data['status'],
            'species': data['species'],
            'type': data.get('type', ''),
            'gender': data.get('gender', ''),
            'origin': data.get('origin', {}),
            'location': location_data,
            'image': data.get('image', ''),
            'episode': episode_urls,
            'created': data.get('created', '')
        }
        
        return Character.from_dict(char_dict)
    
    def _parse_location(self, data: Dict[str, Any]) -> Location:
        """Parse location data from GraphQL response."""
        # Convert residents list to URL format for compatibility
        residents = data.get('residents', [])
        resident_urls = [f"{Config.REST_BASE_URL}/character/{res['id']}" for res in residents]
        
        loc_dict = {
            'id': int(data['id']),
            'name': data['name'],
            'type': data['type'],
            'dimension': data['dimension'],
            'residents': resident_urls,
            'created': data.get('created', '')
        }
        
        return Location.from_dict(loc_dict)
    
    # Override base class methods to provide GraphQL-specific information
    
    def _supports_batch_queries(self) -> bool:
        """GraphQL supports fetching multiple resources in single queries."""
        return True
    
    def _supports_relationship_optimization(self) -> bool:
        """GraphQL can fetch related data in single queries."""
        return True
    
    def _estimate_api_calls(self) -> int:
        """Estimate API calls needed for full dataset."""
        # With ultra-optimization: ~42 calls (vs 49 original)
        return 42
    
    def _get_performance_characteristics(self) -> Dict[str, str]:
        """Describe GraphQL performance characteristics."""
        return {
            'latency': 'Higher per request (complex queries)',
            'throughput': 'Medium to High',
            'optimization_level': 'Ultra-optimized combined queries',
            'caching': 'Query-level caching possible',
            'complexity': 'Complex but powerful'
        }
    
    def get_optimization_modes(self) -> Dict[str, str]:
        """Get available GraphQL optimization modes."""
        return {
            'standard': 'Traditional pagination (49 API calls)',
            'optimized': 'Single query for first page only (1 API call)',
            'ultra_optimized': 'Combined queries for full dataset (~42 API calls)'
        }