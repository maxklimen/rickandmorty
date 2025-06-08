"""Unified data processing for Rick and Morty API data.

This module provides common data processing functionality that works
with data from any API implementation (REST, GraphQL, etc.).
"""
from typing import List, Dict, Any, Optional
from collections import Counter
import logging

from .models import Character, Location
from .utils import setup_logging

logger = setup_logging(__name__)

class DataProcessor:
    """Processes and analyzes Rick and Morty API data from any source."""
    
    def __init__(self):
        """Initialize the data processor."""
        self.logger = setup_logging(f"{__name__}.DataProcessor")
    
    def get_statistics(self, characters: List[Character], locations: List[Location]) -> Dict[str, Any]:
        """Generate comprehensive statistics from characters and locations data.
        
        Args:
            characters: List of Character objects
            locations: List of Location objects
            
        Returns:
            Dictionary containing various statistics and analysis
        """
        self.logger.info(f"Generating statistics for {len(characters)} characters and {len(locations)} locations")
        
        stats = {
            'total_characters': len(characters),
            'total_locations': len(locations),
            'character_status': self._analyze_character_status(characters),
            'character_species': self._analyze_character_species(characters),
            'character_gender': self._analyze_character_gender(characters),
            'location_types': self._analyze_location_types(locations),
            'location_dimensions': self._analyze_location_dimensions(locations),
            'most_populated_locations': self._get_most_populated_locations(locations),
            'character_location_mapping': self._analyze_character_location_mapping(characters, locations),
            'data_quality': self._assess_data_quality(characters, locations)
        }
        
        self.logger.info("Statistics generation completed")
        return stats
    
    def filter_characters(
        self,
        characters: List[Character],
        status: Optional[str] = None,
        species: Optional[str] = None,
        gender: Optional[str] = None,
        location_name: Optional[str] = None
    ) -> List[Character]:
        """Filter characters based on various criteria.
        
        Args:
            characters: List of Character objects to filter
            status: Filter by status (Alive, Dead, unknown)
            species: Filter by species
            gender: Filter by gender
            location_name: Filter by current location name
            
        Returns:
            Filtered list of Character objects
        """
        filtered = characters
        
        if status:
            filtered = [c for c in filtered if c.status.lower() == status.lower()]
            
        if species:
            filtered = [c for c in filtered if c.species.lower() == species.lower()]
            
        if gender:
            filtered = [c for c in filtered if c.gender.lower() == gender.lower()]
            
        if location_name:
            filtered = [c for c in filtered if c.location.get('name', '').lower() == location_name.lower()]
        
        self.logger.info(f"Filtered {len(characters)} characters to {len(filtered)} results")
        return filtered
    
    def filter_locations(
        self,
        locations: List[Location],
        type_filter: Optional[str] = None,
        dimension: Optional[str] = None,
        min_residents: Optional[int] = None
    ) -> List[Location]:
        """Filter locations based on various criteria.
        
        Args:
            locations: List of Location objects to filter
            type_filter: Filter by location type
            dimension: Filter by dimension
            min_residents: Filter by minimum number of residents
            
        Returns:
            Filtered list of Location objects
        """
        filtered = locations
        
        if type_filter:
            filtered = [l for l in filtered if l.type.lower() == type_filter.lower()]
            
        if dimension:
            filtered = [l for l in filtered if l.dimension.lower() == dimension.lower()]
            
        if min_residents is not None:
            filtered = [l for l in filtered if len(l.residents) >= min_residents]
        
        self.logger.info(f"Filtered {len(locations)} locations to {len(filtered)} results")
        return filtered
    
    def _analyze_character_status(self, characters: List[Character]) -> Dict[str, int]:
        """Analyze character status distribution."""
        status_counts = Counter(char.status for char in characters)
        return dict(status_counts.most_common())
    
    def _analyze_character_species(self, characters: List[Character]) -> Dict[str, int]:
        """Analyze character species distribution."""
        species_counts = Counter(char.species for char in characters)
        return dict(species_counts.most_common())
    
    def _analyze_character_gender(self, characters: List[Character]) -> Dict[str, int]:
        """Analyze character gender distribution."""
        gender_counts = Counter(char.gender for char in characters)
        return dict(gender_counts.most_common())
    
    def _analyze_location_types(self, locations: List[Location]) -> Dict[str, int]:
        """Analyze location type distribution."""
        type_counts = Counter(loc.type for loc in locations)
        return dict(type_counts.most_common())
    
    def _analyze_location_dimensions(self, locations: List[Location]) -> Dict[str, int]:
        """Analyze location dimension distribution."""
        dimension_counts = Counter(loc.dimension for loc in locations)
        return dict(dimension_counts.most_common())
    
    def _get_most_populated_locations(self, locations: List[Location]) -> List[Dict[str, Any]]:
        """Get locations sorted by resident count."""
        populated_locations = [
            {
                'name': loc.name,
                'type': loc.type,
                'dimension': loc.dimension,
                'resident_count': len(loc.residents)
            }
            for loc in locations
        ]
        
        # Sort by resident count descending
        populated_locations.sort(key=lambda x: x['resident_count'], reverse=True)
        return populated_locations
    
    def _analyze_character_location_mapping(
        self, 
        characters: List[Character], 
        locations: List[Location]
    ) -> Dict[str, Any]:
        """Analyze character-location relationships."""
        location_map = {loc.id: loc for loc in locations}
        
        characters_with_location = 0
        characters_with_valid_location = 0
        location_id_issues = []
        
        for char in characters:
            if char.location and char.location.get('name'):
                characters_with_location += 1
                
                location_id = char.get_location_id()
                if location_id and location_id in location_map:
                    characters_with_valid_location += 1
                elif location_id:
                    location_id_issues.append({
                        'character_id': char.id,
                        'character_name': char.name,
                        'location_id': location_id,
                        'location_url': char.location.get('url', '')
                    })
        
        return {
            'total_characters': len(characters),
            'characters_with_location': characters_with_location,
            'characters_with_valid_location_mapping': characters_with_valid_location,
            'mapping_success_rate': (characters_with_valid_location / len(characters) * 100) if characters else 0,
            'location_id_issues': location_id_issues[:5]  # First 5 issues for debugging
        }
    
    def _assess_data_quality(
        self, 
        characters: List[Character], 
        locations: List[Location]
    ) -> Dict[str, Any]:
        """Assess overall data quality and completeness."""
        character_issues = {
            'missing_origin': len([c for c in characters if not c.origin.name]),
            'missing_location': len([c for c in characters if not c.location.get('name')]),
            'missing_species': len([c for c in characters if not c.species]),
            'unknown_status': len([c for c in characters if c.status == 'unknown'])
        }
        
        location_issues = {
            'missing_type': len([l for l in locations if not l.type]),
            'missing_dimension': len([l for l in locations if not l.dimension]),
            'no_residents': len([l for l in locations if not l.residents]),
            'empty_names': len([l for l in locations if not l.name])
        }
        
        return {
            'character_data_quality': character_issues,
            'location_data_quality': location_issues,
            'overall_completeness_score': self._calculate_completeness_score(character_issues, location_issues, len(characters), len(locations))
        }
    
    def _calculate_completeness_score(
        self, 
        char_issues: Dict[str, int], 
        loc_issues: Dict[str, int],
        total_chars: int,
        total_locs: int
    ) -> float:
        """Calculate overall data completeness score (0-100)."""
        if total_chars == 0 and total_locs == 0:
            return 0.0
        
        total_char_issues = sum(char_issues.values())
        total_loc_issues = sum(loc_issues.values())
        
        # Weight by total number of records
        char_completeness = ((total_chars * 4 - total_char_issues) / (total_chars * 4)) if total_chars > 0 else 1.0
        loc_completeness = ((total_locs * 4 - total_loc_issues) / (total_locs * 4)) if total_locs > 0 else 1.0
        
        # Overall score weighted by dataset size
        overall_score = (char_completeness * total_chars + loc_completeness * total_locs) / (total_chars + total_locs)
        
        return round(overall_score * 100, 2)