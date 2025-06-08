"""Workflow manager for Rick and Morty API operations.

This module orchestrates the complete workflow from data fetching through
processing to export, providing a unified interface for all implementations.
"""
import logging
import time
import sys
from typing import Dict, Any, List, Optional

from .base_client import BaseAPIClient
from .data_processor import DataProcessor
from .csv_exporter import CSVExporter
from .enhanced_csv_exporter import EnhancedCSVExporter
from .argument_parser import CLIMode
from .utils import setup_logging
from .config import Config

logger = setup_logging(__name__)

class APIWorkflowManager:
    """Manages the complete API workflow for any implementation."""
    
    def __init__(self, client: BaseAPIClient, processor: DataProcessor):
        """Initialize the workflow manager.
        
        Args:
            client: API client implementation
            processor: Data processor instance
        """
        self.client = client
        self.processor = processor
        self.logger = setup_logging(f"{__name__}.{client.implementation_type.value}")
    
    def execute_workflow(self, config: Dict[str, Any]) -> int:
        """Execute the complete workflow based on configuration.
        
        Args:
            config: Configuration dictionary from argument parser
            
        Returns:
            Exit code (0 for success, 1 for error)
        """
        try:
            start_time = time.time()
            
            # Configure logging
            self._configure_logging(config)
            
            # Log workflow start
            self._log_workflow_start(config)
            
            # Execute based on mode
            mode = config['mode']
            
            if mode == CLIMode.SINGLE_CHARACTER:
                return self._execute_single_character_workflow(config)
            elif mode == CLIMode.STATISTICS_ONLY:
                return self._execute_statistics_workflow(config)
            elif mode == CLIMode.CHARACTERS_ONLY:
                return self._execute_data_workflow(config, characters_only=True)
            elif mode == CLIMode.LOCATIONS_ONLY:
                return self._execute_data_workflow(config, locations_only=True)
            elif mode == CLIMode.FULL_EXPORT:
                return self._execute_data_workflow(config)
            else:
                raise ValueError(f"Unknown workflow mode: {mode}")
                
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            if config.get('verbose', False):
                self.logger.exception("Full error details:")
            return 1
        finally:
            # Always clean up client resources
            try:
                self.client.close()
            except Exception as e:
                self.logger.warning(f"Error closing client: {e}")
    
    def _execute_single_character_workflow(self, config: Dict[str, Any]) -> int:
        """Execute workflow for single character lookup."""
        character_id = config['character_id']
        
        self.logger.info(f"Fetching character {character_id} with location details")
        
        if config.get('dry_run', False):
            self._print_dry_run_info(f"Would fetch character {character_id}")
            return 0
        
        result = self.client.fetch_character_with_location(character_id)
        character = result['character']
        location = result.get('location')
        
        # Display character information
        if not config.get('quiet', False):
            self._display_character_info(character, location)
        
        return 0
    
    def _execute_statistics_workflow(self, config: Dict[str, Any]) -> int:
        """Execute workflow for statistics generation only."""
        self.logger.info("Fetching data for statistics generation")
        
        if config.get('dry_run', False):
            self._print_dry_run_info("Would fetch all data and generate statistics")
            return 0
        
        # Fetch data
        characters, locations = self._fetch_data(config)
        
        # Generate and display statistics
        if characters or locations:
            stats = self.processor.get_statistics(characters, locations)
            
            if not config.get('quiet', False):
                self._display_statistics(stats, config)
        
        return 0
    
    def _execute_data_workflow(
        self, 
        config: Dict[str, Any],
        characters_only: bool = False,
        locations_only: bool = False
    ) -> int:
        """Execute workflow for data fetching and export."""
        
        if config.get('dry_run', False):
            data_desc = "characters only" if characters_only else "locations only" if locations_only else "all data"
            self._print_dry_run_info(f"Would fetch {data_desc} and export to CSV")
            return 0
        
        # Fetch data
        characters, locations = self._fetch_data(config, characters_only, locations_only)
        
        # Generate statistics if not quiet
        if (characters or locations) and not config.get('quiet', False):
            stats = self.processor.get_statistics(characters, locations)
            self._display_statistics(stats, config)
        
        # Export to CSV unless stats-only mode
        if not config.get('stats_only', False):
            self._export_data(characters, locations, config)
        
        return 0
    
    def _fetch_data(
        self, 
        config: Dict[str, Any],
        characters_only: bool = False,
        locations_only: bool = False
    ) -> tuple[List, List]:
        """Fetch data based on configuration."""
        characters = []
        locations = []
        
        # Determine what to fetch based on config and flags
        fetch_characters = not locations_only
        fetch_locations = not characters_only
        
        # Special handling for GraphQL optimizations
        if config.get('ultra_optimized', False) and hasattr(self.client, 'fetch_all_data_ultra_optimized'):
            self.logger.info("Using ultra-optimized GraphQL data fetch")
            data = self.client.fetch_all_data_ultra_optimized()
            
            if fetch_characters:
                characters = data['characters']
            if fetch_locations:
                locations = data['locations']
            
            # Display optimization results
            if not config.get('quiet', False):
                self._display_optimization_results(data)
        
        elif config.get('optimized', False) and hasattr(self.client, 'fetch_all_data_optimized'):
            self.logger.info("Using optimized GraphQL single query")
            data = self.client.fetch_all_data_optimized()
            
            if fetch_characters:
                characters = data['characters']
            if fetch_locations:
                locations = data['locations']
        
        else:
            # Standard fetch approach
            if fetch_characters:
                self.logger.info("Fetching all characters...")
                characters = self.client.fetch_all_characters()
                self.logger.info(f"Fetched {len(characters)} characters")
            
            if fetch_locations:
                self.logger.info("Fetching all locations...")
                locations = self.client.fetch_all_locations()
                self.logger.info(f"Fetched {len(locations)} locations")
        
        return characters, locations
    
    def _export_data(self, characters: List, locations: List, config: Dict[str, Any]) -> None:
        """Export data to CSV files."""
        format_type = config.get('format', 'enhanced')
        
        self.logger.info(f"Exporting data to {format_type} CSV files...")
        
        results = {}
        
        if format_type == 'enhanced' and characters and locations:
            # Use enhanced exporter for complex relationships
            results = EnhancedCSVExporter.write_enhanced_data(characters, locations)
            
            if not config.get('quiet', False):
                print("\n=== Enhanced Export Results ===")
                for data_type, filepath in results.items():
                    print(f"{data_type.capitalize()} with relationships exported to: {filepath}")
                
                # Create relationship summary
                summary = EnhancedCSVExporter.create_relationship_summary(characters, locations)
                self._display_relationship_summary(summary)
        
        else:
            # Use basic exporter
            if characters:
                results['characters'] = CSVExporter.write_characters(characters)
            if locations:
                results['locations'] = CSVExporter.write_locations(locations)
            
            if not config.get('quiet', False):
                print("\n=== Basic Export Results ===")
                for data_type, filepath in results.items():
                    print(f"{data_type.capitalize()} exported to: {filepath}")
        
        # Validate export
        validation = CSVExporter.validate_csv_files()
        if validation['valid']:
            if not config.get('quiet', False):
                print("\nValidation successful!")
                if 'characters' in validation:
                    print(f"Characters CSV: {validation['characters']['row_count']} rows")
                if 'locations' in validation:
                    print(f"Locations CSV: {validation['locations']['row_count']} rows")
        else:
            self.logger.error("CSV validation failed!")
            raise Exception("CSV export validation failed")
    
    def _configure_logging(self, config: Dict[str, Any]) -> None:
        """Configure logging based on config."""
        if config.get('verbose', False):
            logging.getLogger().setLevel(logging.DEBUG)
        elif config.get('quiet', False):
            logging.getLogger().setLevel(logging.ERROR)
    
    def _log_workflow_start(self, config: Dict[str, Any]) -> None:
        """Log workflow start information."""
        client_info = self.client.get_implementation_info()
        
        self.logger.info(f"Starting {client_info['type']} workflow")
        self.logger.info(f"Mode: {config['mode'].value}")
        
        if config.get('verbose', False):
            self.logger.debug(f"Client: {client_info['class']}")
            self.logger.debug(f"Estimated API calls: {client_info['estimated_api_calls_for_full_dataset']}")
    
    def _display_character_info(self, character, location) -> None:
        """Display single character information."""
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
    
    def _display_statistics(self, stats: Dict[str, Any], config: Dict[str, Any]) -> None:
        """Display statistics information."""
        client_info = self.client.get_implementation_info()
        
        print(f"\n=== Rick and Morty API Statistics ({client_info['type']}) ===")
        print(f"Total Characters: {stats['total_characters']}")
        print(f"Total Locations: {stats['total_locations']}")
        
        # Display method info
        if config.get('ultra_optimized', False):
            print(f"Method: Ultra-optimized combined queries")
        elif config.get('optimized', False):
            print(f"Method: Optimized single query")
        else:
            print(f"Method: Standard pagination")
        
        print("\nCharacter Status Distribution:")
        for status, count in stats['character_status'].items():
            print(f"  {status}: {count}")
        
        print("\nTop 5 Species:")
        for species, count in list(stats['character_species'].items())[:5]:
            print(f"  {species}: {count}")
        
        print("\nTop 5 Most Populated Locations:")
        for loc in stats['most_populated_locations'][:5]:
            print(f"  {loc['name']} ({loc['type']}): {loc['resident_count']} residents")
        
        # Display data quality if verbose
        if config.get('verbose', False):
            self._display_data_quality(stats['data_quality'])
    
    def _display_optimization_results(self, data: Dict[str, Any]) -> None:
        """Display GraphQL optimization results."""
        print(f"\n🚀 Ultra-Optimization Results:")
        print(f"  API Calls Made: {data['api_calls']} (vs 49 original)")
        print(f"  API Call Reduction: {data['optimization_percentage']:.1f}%")
        print(f"  Fetch Time: {data['total_time']:.2f}s")
    
    def _display_relationship_summary(self, summary: Dict[str, Any]) -> None:
        """Display relationship mapping summary."""
        print(f"\n=== Relationship Summary ===")
        print(f"Total Characters: {summary['total_characters']}")
        print(f"Characters with Location: {summary['characters_with_location']}")
        print(f"Total Locations: {summary['total_locations']}")
        print(f"Locations with Residents: {summary['locations_with_residents']}")
    
    def _display_data_quality(self, quality: Dict[str, Any]) -> None:
        """Display data quality assessment."""
        print(f"\n=== Data Quality Assessment ===")
        print(f"Overall Completeness Score: {quality['overall_completeness_score']:.1f}%")
        
        char_issues = quality['character_data_quality']
        print(f"\nCharacter Data Issues:")
        for issue, count in char_issues.items():
            if count > 0:
                print(f"  {issue.replace('_', ' ').title()}: {count}")
        
        loc_issues = quality['location_data_quality']
        print(f"\nLocation Data Issues:")
        for issue, count in loc_issues.items():
            if count > 0:
                print(f"  {issue.replace('_', ' ').title()}: {count}")
    
    def _print_dry_run_info(self, action: str) -> None:
        """Print dry run information."""
        client_info = self.client.get_implementation_info()
        print(f"\n[DRY RUN] {client_info['type']} Implementation")
        print(f"[DRY RUN] {action}")
        print(f"[DRY RUN] Estimated API calls: {client_info['estimated_api_calls_for_full_dataset']}")
        print(f"[DRY RUN] Performance: {client_info['performance_characteristics']}")