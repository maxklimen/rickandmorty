"""REST API main entry point."""
import argparse
import sys
import logging
from typing import Dict, Any

from .rest_client import RESTClient
from .rest_data_processor import RESTDataProcessor
from ..shared.csv_exporter import CSVExporter
from ..shared.enhanced_csv_exporter import EnhancedCSVExporter
from ..shared.utils import setup_logging
from ..shared.config import Config

logger = setup_logging(__name__)

def main():
    """Main entry point for REST implementation."""
    parser = argparse.ArgumentParser(
        description="Rick and Morty REST API Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch all data and export to CSV
  python -m src.rest.rest_main
  
  # Fetch only characters
  python -m src.rest.rest_main --characters-only
  
  # Fetch only locations
  python -m src.rest.rest_main --locations-only
  
  # Get statistics without exporting
  python -m src.rest.rest_main --stats-only
  
  # Fetch specific character with location details
  python -m src.rest.rest_main --character-id 1
        """
    )
    
    parser.add_argument(
        '--characters-only', 
        action='store_true',
        help='Fetch only characters data'
    )
    parser.add_argument(
        '--locations-only', 
        action='store_true',
        help='Fetch only locations data'
    )
    parser.add_argument(
        '--stats-only', 
        action='store_true',
        help='Show statistics without exporting to CSV'
    )
    parser.add_argument(
        '--character-id', 
        type=int,
        help='Fetch specific character with location details'
    )
    parser.add_argument(
        '--output-dir', 
        type=str,
        default=Config.OUTPUT_DIR,
        help='Output directory for CSV files'
    )
    parser.add_argument(
        '--verbose', 
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Update output directory if specified
    if args.output_dir != Config.OUTPUT_DIR:
        Config.OUTPUT_DIR = args.output_dir
    
    try:
        client = RESTClient()
        processor = RESTDataProcessor()
        
        # Handle single character request
        if args.character_id:
            logger.info(f"Fetching character {args.character_id} with location details")
            result = client.fetch_character_with_location(args.character_id)
            
            character = result['character']
            location = result['location']
            
            print(f"\nCharacter: {character.name}")
            print(f"Status: {character.status}")
            print(f"Species: {character.species}")
            print(f"Origin: {character.origin.name}")
            print(f"Current Location: {character.location.get('name', 'Unknown')}")
            
            if location:
                print(f"\nLocation Details:")
                print(f"Type: {location.type}")
                print(f"Dimension: {location.dimension}")
                print(f"Residents: {len(location.residents)}")
            
            client.close()
            return 0
        
        # Fetch data based on arguments
        characters = []
        locations = []
        
        if not args.locations_only:
            logger.info("Fetching all characters...")
            characters = client.fetch_all_characters()
            logger.info(f"Fetched {len(characters)} characters")
        
        if not args.characters_only:
            logger.info("Fetching all locations...")
            locations = client.fetch_all_locations()
            logger.info(f"Fetched {len(locations)} locations")
        
        # Generate and display statistics
        if characters and locations:
            stats = processor.get_statistics(characters, locations)
            
            print("\n=== Rick and Morty API Statistics ===")
            print(f"Total Characters: {stats['total_characters']}")
            print(f"Total Locations: {stats['total_locations']}")
            
            print("\nCharacter Status Distribution:")
            for status, count in stats['character_status'].items():
                print(f"  {status}: {count}")
            
            print("\nTop 5 Species:")
            for species, count in list(stats['character_species'].items())[:5]:
                print(f"  {species}: {count}")
            
            print("\nTop 5 Most Populated Locations:")
            for loc in stats['most_populated_locations'][:5]:
                print(f"  {loc['name']} ({loc['type']}): {loc['resident_count']} residents")
        
        # Export to CSV unless stats-only mode
        if not args.stats_only:
            logger.info("Exporting data to enhanced CSV files with complex relationships...")
            
            if characters and locations:
                # Use enhanced exporter for complex relationships
                results = EnhancedCSVExporter.write_enhanced_data(characters, locations)
                
                print("\n=== Enhanced Export Results ===")
                for data_type, filepath in results.items():
                    print(f"{data_type.capitalize()} with relationships exported to: {filepath}")
                
                # Create relationship summary
                summary = EnhancedCSVExporter.create_relationship_summary(characters, locations)
                print(f"\n=== Relationship Summary ===")
                print(f"Total Characters: {summary['total_characters']}")
                print(f"Characters with Location: {summary['characters_with_location']}")
                print(f"Total Locations: {summary['total_locations']}")
                print(f"Locations with Residents: {summary['locations_with_residents']}")
                
            else:
                # Fallback to basic export if missing data
                results = {}
                if characters:
                    results['characters'] = CSVExporter.write_characters(characters)
                if locations:
                    results['locations'] = CSVExporter.write_locations(locations)
                
                print("\n=== Basic Export Results ===")
                for data_type, filepath in results.items():
                    print(f"{data_type.capitalize()} exported to: {filepath}")
            
            # Validate export
            validation = CSVExporter.validate_csv_files()
            if validation['valid']:
                print("\nValidation successful!")
                print(f"Characters CSV: {validation['characters']['row_count']} rows")
                print(f"Locations CSV: {validation['locations']['row_count']} rows")
            else:
                logger.error("CSV validation failed!")
                return 1
        
        client.close()
        logger.info("REST client execution completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error in REST client: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())