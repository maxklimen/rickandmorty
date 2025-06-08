"""Data processing for REST API responses."""
from typing import List, Dict, Any, Optional
import logging

from ..shared.models import Character, Location
from ..shared.utils import setup_logging

logger = setup_logging(__name__)

class RESTDataProcessor:
    """Process and transform REST API data."""
    
    @staticmethod
    def process_characters(characters: List[Character]) -> List[Dict[str, Any]]:
        """Process characters for export or API response."""
        processed = []
        
        for character in characters:
            try:
                processed.append(character.to_dict())
            except Exception as e:
                logger.error(f"Error processing character {character.id}: {str(e)}")
                continue
        
        return processed
    
    @staticmethod
    def process_locations(locations: List[Location]) -> List[Dict[str, Any]]:
        """Process locations for export or API response."""
        processed = []
        
        for location in locations:
            try:
                processed_location = {
                    'id': location.id,
                    'name': location.name,
                    'type': location.type,
                    'dimension': location.dimension,
                    'resident_count': len(location.residents)
                }
                processed.append(processed_location)
            except Exception as e:
                logger.error(f"Error processing location {location.id}: {str(e)}")
                continue
        
        return processed
    
    @staticmethod
    def enrich_characters_with_locations(
        characters: List[Character], 
        locations: List[Location]
    ) -> List[Dict[str, Any]]:
        """Enrich character data with location information."""
        # Create location lookup map
        location_map = {loc.id: loc for loc in locations}
        
        enriched = []
        for character in characters:
            char_dict = character.to_dict()
            location_id = character.get_location_id()
            
            if location_id and location_id in location_map:
                location = location_map[location_id]
                char_dict['location_details'] = {
                    'type': location.type,
                    'dimension': location.dimension,
                    'resident_count': len(location.residents)
                }
            else:
                char_dict['location_details'] = None
            
            enriched.append(char_dict)
        
        return enriched
    
    @staticmethod
    def get_statistics(characters: List[Character], locations: List[Location]) -> Dict[str, Any]:
        """Generate statistics from the data."""
        # Character statistics
        status_counts = {}
        species_counts = {}
        
        for char in characters:
            status_counts[char.status] = status_counts.get(char.status, 0) + 1
            species_counts[char.species] = species_counts.get(char.species, 0) + 1
        
        # Location statistics
        type_counts = {}
        dimension_counts = {}
        
        for loc in locations:
            type_counts[loc.type] = type_counts.get(loc.type, 0) + 1
            dimension_counts[loc.dimension] = dimension_counts.get(loc.dimension, 0) + 1
        
        # Find most populated locations
        locations_by_residents = sorted(
            locations, 
            key=lambda x: len(x.residents), 
            reverse=True
        )[:10]
        
        return {
            'total_characters': len(characters),
            'total_locations': len(locations),
            'character_status': status_counts,
            'character_species': dict(sorted(
                species_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]),
            'location_types': type_counts,
            'location_dimensions': dict(sorted(
                dimension_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]),
            'most_populated_locations': [
                {
                    'name': loc.name,
                    'resident_count': len(loc.residents),
                    'type': loc.type,
                    'dimension': loc.dimension
                }
                for loc in locations_by_residents
            ]
        }
    
    @staticmethod
    def filter_characters(
        characters: List[Character],
        status: Optional[str] = None,
        species: Optional[str] = None,
        origin_name: Optional[str] = None
    ) -> List[Character]:
        """Filter characters based on criteria."""
        filtered = characters
        
        if status:
            filtered = [c for c in filtered if c.status.lower() == status.lower()]
        
        if species:
            filtered = [c for c in filtered if c.species.lower() == species.lower()]
        
        if origin_name:
            filtered = [c for c in filtered if origin_name.lower() in c.origin.name.lower()]
        
        return filtered
    
    @staticmethod
    def filter_locations(
        locations: List[Location],
        type_filter: Optional[str] = None,
        dimension: Optional[str] = None,
        min_residents: Optional[int] = None
    ) -> List[Location]:
        """Filter locations based on criteria."""
        filtered = locations
        
        if type_filter:
            filtered = [l for l in filtered if l.type.lower() == type_filter.lower()]
        
        if dimension:
            filtered = [l for l in filtered if dimension.lower() in l.dimension.lower()]
        
        if min_residents is not None:
            filtered = [l for l in filtered if len(l.residents) >= min_residents]
        
        return filtered