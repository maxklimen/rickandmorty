"""Enhanced CSV export functionality with complex relationships for Rick and Morty data."""
import csv
import os
from typing import List, Dict, Any, Optional
import logging

from .models import Character, Location
from .config import Config
from .utils import setup_logging, chunks, extract_id_from_url

logger = setup_logging(__name__)

class EnhancedCSVExporter:
    """Handle CSV export operations with complex relationship mapping."""
    
    @staticmethod
    def write_enhanced_characters(
        characters: List[Character], 
        locations: List[Location],
        filepath: str = None
    ) -> str:
        """Write characters to CSV with full location details."""
        filepath = filepath or Config.get_character_csv_path()
        
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Create location lookup map for efficient access
            location_map = {loc.id: loc for loc in locations}
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(Config.CHARACTER_CSV_HEADERS)
                
                # Process in chunks for memory efficiency
                for chunk in chunks(characters, Config.CHUNK_SIZE):
                    rows = []
                    for char in chunk:
                        # Get location details if available
                        location_details = None
                        location_id = char.get_location_id()
                        if location_id and location_id in location_map:
                            location = location_map[location_id]
                            location_details = {
                                'name': location.name,
                                'type': location.type,
                                'dimension': location.dimension
                            }
                        
                        row = char.to_csv_row(location_details)
                        rows.append(row)
                    
                    writer.writerows(rows)
            
            logger.info(f"Successfully wrote {len(characters)} characters with location details to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to write enhanced characters CSV: {str(e)}")
            raise
    
    @staticmethod
    def write_enhanced_locations(
        locations: List[Location], 
        characters: List[Character],
        filepath: str = None
    ) -> str:
        """Write locations to CSV with resident character names."""
        filepath = filepath or Config.get_location_csv_path()
        
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Create character lookup map for efficient access
            character_map = {char.id: char.name for char in characters}
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(Config.LOCATION_CSV_HEADERS)
                
                # Process in chunks for memory efficiency
                for chunk in chunks(locations, Config.CHUNK_SIZE):
                    rows = []
                    for location in chunk:
                        # Extract character names from resident URLs
                        character_names = []
                        for resident_url in location.residents:
                            char_id = extract_id_from_url(resident_url, "character")
                            if char_id and char_id in character_map:
                                character_names.append(character_map[char_id])
                        
                        # Limit character names to prevent CSV cell overflow
                        if len(character_names) > 20:
                            character_names = character_names[:20] + [f"... and {len(character_names) - 20} more"]
                        
                        row = location.to_csv_row(character_names)
                        rows.append(row)
                    
                    writer.writerows(rows)
            
            logger.info(f"Successfully wrote {len(locations)} locations with resident details to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to write enhanced locations CSV: {str(e)}")
            raise
    
    @staticmethod
    def write_enhanced_data(
        characters: List[Character], 
        locations: List[Location]
    ) -> Dict[str, str]:
        """Write both enhanced characters and locations CSV files."""
        logger.info("Writing enhanced CSV files with complex relationships...")
        
        results = {}
        
        try:
            # Write enhanced characters CSV
            results['characters'] = EnhancedCSVExporter.write_enhanced_characters(
                characters, locations
            )
            
            # Write enhanced locations CSV
            results['locations'] = EnhancedCSVExporter.write_enhanced_locations(
                locations, characters
            )
            
            logger.info("Successfully exported enhanced CSV files")
            return results
            
        except Exception as e:
            logger.error(f"Failed to write enhanced CSV files: {str(e)}")
            raise
    
    @staticmethod
    def create_relationship_summary(
        characters: List[Character], 
        locations: List[Location]
    ) -> Dict[str, Any]:
        """Create a summary of relationships for validation."""
        logger.info("Creating relationship summary...")
        
        # Character → Location relationships
        char_location_map = {}
        location_char_counts = {}
        
        for char in characters:
            location_id = char.get_location_id()
            if location_id:
                char_location_map[char.id] = location_id
                location_char_counts[location_id] = location_char_counts.get(location_id, 0) + 1
        
        # Location → Character relationships
        location_residents = {}
        for location in locations:
            resident_count = 0
            resident_names = []
            
            for resident_url in location.residents:
                char_id = extract_id_from_url(resident_url, "character")
                if char_id:
                    resident_count += 1
                    # Find character name
                    char = next((c for c in characters if c.id == char_id), None)
                    if char:
                        resident_names.append(char.name)
            
            location_residents[location.id] = {
                'name': location.name,
                'resident_count': resident_count,
                'residents_in_csv': len(resident_names),
                'sample_residents': resident_names[:5]  # First 5 for preview
            }
        
        return {
            'total_characters': len(characters),
            'total_locations': len(locations),
            'characters_with_location': len(char_location_map),
            'locations_with_residents': len([l for l in location_residents.values() if l['resident_count'] > 0]),
            'character_location_mapping': dict(list(char_location_map.items())[:5]),  # Sample
            'location_resident_summary': dict(list(location_residents.items())[:5])   # Sample
        }