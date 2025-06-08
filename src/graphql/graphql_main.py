"""GraphQL API main entry point."""
import argparse
import sys
import logging
import time

from .graphql_client import GraphQLClient
from ..rest.rest_data_processor import RESTDataProcessor
from ..shared.csv_exporter import CSVExporter
from ..shared.utils import setup_logging
from ..shared.config import Config

logger = setup_logging(__name__)

def main():
    """Main entry point for GraphQL implementation."""
    parser = argparse.ArgumentParser(
        description="Rick and Morty GraphQL API Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch all data and export to CSV
  python -m src.graphql.graphql_main
  
  # Fetch only characters
  python -m src.graphql.graphql_main --characters-only
  
  # Fetch only locations
  python -m src.graphql.graphql_main --locations-only
  
  # Get statistics without exporting
  python -m src.graphql.graphql_main --stats-only
  
  # Fetch specific character with location details
  python -m src.graphql.graphql_main --character-id 1
  
  # Use optimized single query for first page
  python -m src.graphql.graphql_main --optimized
  
  # Use ultra-optimized combined queries (85% fewer API calls)
  python -m src.graphql.graphql_main --ultra-optimized
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
        '--optimized', 
        action='store_true',
        help='Use optimized single query (first page only)'
    )
    parser.add_argument(
        '--ultra-optimized', 
        action='store_true',
        help='Use ultra-optimized combined queries (full dataset with ~85% fewer API calls)'
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
        start_time = time.time()
        client = GraphQLClient()
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
                print(f"\nLocation Details (fetched in same query):")
                print(f"Type: {location.type}")
                print(f"Dimension: {location.dimension}")
                print(f"Residents: {len(location.residents)}")
            
            elapsed = time.time() - start_time
            print(f"\nCompleted in {elapsed:.2f} seconds")
            return 0
        
        # Fetch data based on arguments
        characters = []
        locations = []
        
        if args.ultra_optimized:
            # Use ultra-optimized combined queries
            logger.info("Using ultra-optimized GraphQL queries...")
            data = client.fetch_all_data_ultra_optimized()
            if not args.locations_only:
                characters = data['characters']
            if not args.characters_only:
                locations = data['locations']
            
            # Display optimization results
            print(f"\n🚀 Ultra-Optimization Results:")
            print(f"  API Calls Made: {data['api_calls']} (vs 49 original)")
            print(f"  API Call Reduction: {data['optimization_percentage']:.1f}%")
            print(f"  Fetch Time: {data['total_time']:.2f}s")
            
        elif args.optimized:
            # Use optimized single query
            logger.info("Using optimized GraphQL query...")
            data = client.fetch_all_data_optimized()
            if not args.locations_only:
                characters = data['characters']
            if not args.characters_only:
                locations = data['locations']
        else:
            # Standard pagination approach
            if not args.locations_only:
                logger.info("Fetching all characters via GraphQL...")
                characters = client.fetch_all_characters()
                logger.info(f"Fetched {len(characters)} characters")
            
            if not args.characters_only:
                logger.info("Fetching all locations via GraphQL...")
                locations = client.fetch_all_locations()
                logger.info(f"Fetched {len(locations)} locations")
        
        # Calculate performance metrics
        elapsed = time.time() - start_time
        
        # Generate and display statistics
        if characters and locations:
            stats = processor.get_statistics(characters, locations)
            
            print("\n=== Rick and Morty API Statistics (GraphQL) ===")
            print(f"Total Characters: {stats['total_characters']}")
            print(f"Total Locations: {stats['total_locations']}")
            print(f"\nFetch Time: {elapsed:.2f} seconds")
            method = 'Ultra-optimized combined queries' if args.ultra_optimized else ('Optimized single query' if args.optimized else 'Standard pagination')
            print(f"Method: {method}")
            
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
            logger.info("Exporting data to CSV files...")
            
            results = {}
            if characters:
                results['characters'] = CSVExporter.write_characters(characters)
            if locations:
                results['locations'] = CSVExporter.write_locations(locations)
            
            print("\n=== Export Results ===")
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
        
        total_elapsed = time.time() - start_time
        print(f"\nTotal execution time: {total_elapsed:.2f} seconds")
        
        logger.info("GraphQL client execution completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error in GraphQL client: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())