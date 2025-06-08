"""CSV export functionality for Rick and Morty data."""
import csv
import os
from typing import List, Union, Dict, Any
import logging

from .models import Character, Location
from .config import Config
from .utils import setup_logging, chunks

logger = setup_logging(__name__)

class CSVExporter:
    """Handle CSV export operations."""
    
    @staticmethod
    def write_characters(characters: List[Character], filepath: str = None) -> str:
        """Write characters to CSV file."""
        filepath = filepath or Config.get_character_csv_path()
        
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(Config.CHARACTER_CSV_HEADERS)
                
                # Process in chunks for memory efficiency
                for chunk in chunks(characters, Config.CHUNK_SIZE):
                    rows = [char.to_csv_row() for char in chunk]
                    writer.writerows(rows)
            
            logger.info(f"Successfully wrote {len(characters)} characters to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to write characters CSV: {str(e)}")
            raise
    
    @staticmethod
    def write_locations(locations: List[Location], filepath: str = None) -> str:
        """Write locations to CSV file."""
        filepath = filepath or Config.get_location_csv_path()
        
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(Config.LOCATION_CSV_HEADERS)
                
                # Process in chunks for memory efficiency
                for chunk in chunks(locations, Config.CHUNK_SIZE):
                    rows = [loc.to_csv_row() for loc in chunk]
                    writer.writerows(rows)
            
            logger.info(f"Successfully wrote {len(locations)} locations to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to write locations CSV: {str(e)}")
            raise
    
    @staticmethod
    def write_combined_data(data: Dict[str, List[Union[Character, Location]]]) -> Dict[str, str]:
        """Write both characters and locations to CSV files."""
        results = {}
        
        if 'characters' in data:
            results['characters'] = CSVExporter.write_characters(data['characters'])
        
        if 'locations' in data:
            results['locations'] = CSVExporter.write_locations(data['locations'])
        
        return results
    
    @staticmethod
    def append_characters(characters: List[Character], filepath: str = None) -> str:
        """Append characters to existing CSV file."""
        filepath = filepath or Config.get_character_csv_path()
        
        try:
            # Check if file exists and has headers
            file_exists = os.path.exists(filepath)
            
            with open(filepath, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write headers if new file
                if not file_exists:
                    writer.writerow(Config.CHARACTER_CSV_HEADERS)
                
                # Write character data
                for character in characters:
                    writer.writerow(character.to_csv_row())
            
            logger.info(f"Appended {len(characters)} characters to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to append characters to CSV: {str(e)}")
            raise
    
    @staticmethod
    def validate_csv_files() -> Dict[str, Any]:
        """Validate that CSV files exist and contain data."""
        results = {
            'valid': True,
            'characters': {'exists': False, 'row_count': 0},
            'locations': {'exists': False, 'row_count': 0}
        }
        
        # Check characters CSV
        char_path = Config.get_character_csv_path()
        if os.path.exists(char_path):
            results['characters']['exists'] = True
            with open(char_path, 'r') as f:
                row_count = sum(1 for _ in f) - 1  # Subtract header
                results['characters']['row_count'] = max(0, row_count)
        else:
            results['valid'] = False
        
        # Check locations CSV
        loc_path = Config.get_location_csv_path()
        if os.path.exists(loc_path):
            results['locations']['exists'] = True
            with open(loc_path, 'r') as f:
                row_count = sum(1 for _ in f) - 1  # Subtract header
                results['locations']['row_count'] = max(0, row_count)
        else:
            results['valid'] = False
        
        return results