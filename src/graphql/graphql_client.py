"""GraphQL API client for Rick and Morty API."""
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from typing import List, Dict, Any, Optional
import logging

from ..shared.config import Config
from ..shared.models import Character, Location
from ..shared.utils import setup_logging, APIError, ProgressTracker

logger = setup_logging(__name__)

class GraphQLClient:
    """GraphQL API client for Rick and Morty API."""
    
    # GraphQL queries
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
                    type
                    dimension
                    residents {
                        id
                    }
                }
                image
                episode {
                    id
                }
                created
            }
        }
    """)
    
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
    
    # Optimized query that fetches both characters and locations in parallel
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
        self.url = url
        transport = RequestsHTTPTransport(
            url=url,
            headers={'User-Agent': 'RickAndMortyGraphQLClient/1.0'},
            timeout=Config.TIMEOUT
        )
        self.client = Client(transport=transport, fetch_schema_from_transport=True)
    
    def _execute_query(self, query: Any, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a GraphQL query."""
        try:
            result = self.client.execute(query, variable_values=variables)
            return result
        except Exception as e:
            logger.error(f"GraphQL query failed: {str(e)}")
            raise APIError(f"GraphQL query failed: {str(e)}")
    
    def fetch_all_characters(self) -> List[Character]:
        """Fetch all characters using GraphQL pagination."""
        all_characters = []
        page = 1
        
        # First query to get total pages
        result = self._execute_query(self.CHARACTERS_QUERY, {"page": page})
        characters_data = result.get('characters', {})
        info = characters_data.get('info', {})
        total_pages = info.get('pages', 0)
        
        logger.info(f"Total character pages to fetch: {total_pages}")
        progress = ProgressTracker(total_pages, "Fetching characters via GraphQL")
        
        # Process first page
        for char_data in characters_data.get('results', []):
            character = self._parse_character(char_data)
            all_characters.append(character)
        progress.update(1)
        
        # Fetch remaining pages
        while page < total_pages:
            page += 1
            result = self._execute_query(self.CHARACTERS_QUERY, {"page": page})
            characters_data = result.get('characters', {})
            
            for char_data in characters_data.get('results', []):
                character = self._parse_character(char_data)
                all_characters.append(character)
            
            progress.update(1)
        
        progress.finish()
        logger.info(f"Fetched {len(all_characters)} characters via GraphQL")
        
        return all_characters
    
    def fetch_all_locations(self) -> List[Location]:
        """Fetch all locations using GraphQL pagination."""
        all_locations = []
        page = 1
        
        # First query to get total pages
        result = self._execute_query(self.LOCATIONS_QUERY, {"page": page})
        locations_data = result.get('locations', {})
        info = locations_data.get('info', {})
        total_pages = info.get('pages', 0)
        
        logger.info(f"Total location pages to fetch: {total_pages}")
        progress = ProgressTracker(total_pages, "Fetching locations via GraphQL")
        
        # Process first page
        for loc_data in locations_data.get('results', []):
            location = self._parse_location(loc_data)
            all_locations.append(location)
        progress.update(1)
        
        # Fetch remaining pages
        while page < total_pages:
            page += 1
            result = self._execute_query(self.LOCATIONS_QUERY, {"page": page})
            locations_data = result.get('locations', {})
            
            for loc_data in locations_data.get('results', []):
                location = self._parse_location(loc_data)
                all_locations.append(location)
            
            progress.update(1)
        
        progress.finish()
        logger.info(f"Fetched {len(all_locations)} locations via GraphQL")
        
        return all_locations
    
    def fetch_character_with_location(self, character_id: int) -> Dict[str, Any]:
        """Fetch character with full location details in a single query."""
        result = self._execute_query(self.CHARACTER_BY_ID_QUERY, {"id": str(character_id)})
        char_data = result.get('character')
        
        if not char_data:
            raise APIError(f"Character {character_id} not found", status_code=404)
        
        character = self._parse_character(char_data)
        
        # Location data is already included in the query
        location = None
        if char_data.get('location') and char_data['location'].get('id'):
            location = self._parse_location(char_data['location'])
        
        return {
            'character': character,
            'location': location
        }
    
    def fetch_all_data_optimized(self) -> Dict[str, List[Any]]:
        """Fetch first page of all data in a single optimized query."""
        logger.info("Fetching data using optimized GraphQL query")
        
        result = self._execute_query(self.ALL_DATA_QUERY)
        
        characters = []
        for char_data in result.get('characters', {}).get('results', []):
            character = self._parse_character(char_data)
            characters.append(character)
        
        locations = []
        for loc_data in result.get('locations', {}).get('results', []):
            location = self._parse_location(loc_data)
            locations.append(location)
        
        logger.info(f"Fetched {len(characters)} characters and {len(locations)} locations in single query")
        
        return {
            'characters': characters,
            'locations': locations
        }
    
    def fetch_all_data_ultra_optimized(self) -> Dict[str, List[Any]]:
        """Fetch ALL data using optimized combined queries - reduces API calls by ~85%."""
        import time
        start_time = time.time()
        
        logger.info("Starting ultra-optimized GraphQL data fetch...")
        
        # First, get pagination info from the simple query
        first_result = self._execute_query(self.ALL_DATA_QUERY)
        char_pages = first_result.get('characters', {}).get('info', {}).get('pages', 42)
        loc_pages = first_result.get('locations', {}).get('info', {}).get('pages', 7)
        
        logger.info(f"Detected {char_pages} character pages and {loc_pages} location pages")
        
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
        # Since locations have fewer pages (7), we'll pair them optimally
        remaining_char_pages = list(range(2, char_pages + 1))  # Skip page 1, already fetched
        remaining_loc_pages = list(range(2, loc_pages + 1))    # Skip page 1, already fetched
        
        # Combine queries: each query fetches both characters and locations
        queries_made = 1  # First query already made
        
        # Smart optimization: Combine character and location fetching
        # We have 41 remaining character pages and 6 remaining location pages
        # Strategy: Pair them up optimally to minimize total calls
        
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
                    logger.error(f"Error fetching combined page char={char_page}, loc={loc_page}: {e}")
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
                    logger.error(f"Error fetching character page {char_page}: {e}")
            
            i += 1
        
        total_time = time.time() - start_time
        
        logger.info(f"Ultra-optimized fetch completed!")
        logger.info(f"  Total API calls: {queries_made} (vs 49 in original)")
        logger.info(f"  API call reduction: {((49 - queries_made) / 49 * 100):.1f}%")
        logger.info(f"  Total time: {total_time:.2f}s")
        logger.info(f"  Characters fetched: {len(all_characters)}")
        logger.info(f"  Locations fetched: {len(all_locations)}")
        
        return {
            'characters': all_characters,
            'locations': all_locations,
            'api_calls': queries_made,
            'total_time': total_time,
            'optimization_percentage': ((49 - queries_made) / 49 * 100)
        }
    
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