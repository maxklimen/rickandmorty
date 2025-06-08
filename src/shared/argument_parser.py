"""Unified CLI argument parsing for Rick and Morty API clients."""
import argparse
from typing import Dict, Any, Optional
from enum import Enum

from .config import Config
from .base_client import APIImplementationType

class CLIMode(Enum):
    """CLI operation modes."""
    FULL_EXPORT = "full_export"
    CHARACTERS_ONLY = "characters_only"
    LOCATIONS_ONLY = "locations_only"
    STATISTICS_ONLY = "statistics_only"
    SINGLE_CHARACTER = "single_character"

class CLIArgumentParser:
    """Centralized argument parsing for all API implementations."""
    
    @staticmethod
    def create_parser(implementation_type: APIImplementationType) -> argparse.ArgumentParser:
        """Create argument parser for specific implementation type.
        
        Args:
            implementation_type: The API implementation type
            
        Returns:
            Configured ArgumentParser instance
        """
        impl_name = implementation_type.value
        
        parser = argparse.ArgumentParser(
            description=f"Rick and Morty {impl_name} API Client",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=CLIArgumentParser._get_examples(implementation_type)
        )
        
        # Common arguments for all implementations
        CLIArgumentParser._add_common_arguments(parser)
        
        # Implementation-specific arguments
        if implementation_type == APIImplementationType.GRAPHQL:
            CLIArgumentParser._add_graphql_arguments(parser)
        elif implementation_type == APIImplementationType.REST:
            CLIArgumentParser._add_rest_arguments(parser)
        
        return parser
    
    @staticmethod
    def _add_common_arguments(parser: argparse.ArgumentParser) -> None:
        """Add arguments common to all implementations."""
        
        # Data selection arguments
        data_group = parser.add_argument_group('Data Selection')
        data_group.add_argument(
            '--characters-only', 
            action='store_true',
            help='Fetch only characters data'
        )
        data_group.add_argument(
            '--locations-only', 
            action='store_true',
            help='Fetch only locations data'
        )
        data_group.add_argument(
            '--stats-only', 
            action='store_true',
            help='Show statistics without exporting to CSV'
        )
        data_group.add_argument(
            '--character-id', 
            type=int,
            metavar='ID',
            help='Fetch specific character with location details'
        )
        
        # Output arguments
        output_group = parser.add_argument_group('Output Options')
        output_group.add_argument(
            '--output-dir', 
            type=str,
            default=Config.OUTPUT_DIR,
            metavar='PATH',
            help=f'Output directory for CSV files (default: {Config.OUTPUT_DIR})'
        )
        output_group.add_argument(
            '--format',
            choices=['basic', 'enhanced'],
            default='enhanced',
            help='CSV output format: basic or enhanced with relationships (default: enhanced)'
        )
        
        # Execution arguments
        exec_group = parser.add_argument_group('Execution Options')
        exec_group.add_argument(
            '--verbose', 
            action='store_true',
            help='Enable verbose logging'
        )
        exec_group.add_argument(
            '--quiet', 
            action='store_true',
            help='Suppress all output except errors'
        )
        exec_group.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without executing'
        )
    
    @staticmethod
    def _add_graphql_arguments(parser: argparse.ArgumentParser) -> None:
        """Add GraphQL-specific arguments."""
        graphql_group = parser.add_argument_group('GraphQL Options')
        graphql_group.add_argument(
            '--optimized', 
            action='store_true',
            help='Use optimized single query (first page only, demo mode)'
        )
        graphql_group.add_argument(
            '--ultra-optimized', 
            action='store_true',
            help='Use ultra-optimized combined queries (full dataset with fewer API calls)'
        )
        graphql_group.add_argument(
            '--query-complexity',
            choices=['simple', 'complex', 'ultra'],
            default='simple',
            help='GraphQL query complexity level (default: simple)'
        )
    
    @staticmethod
    def _add_rest_arguments(parser: argparse.ArgumentParser) -> None:
        """Add REST-specific arguments."""
        rest_group = parser.add_argument_group('REST Options')
        rest_group.add_argument(
            '--batch-size',
            type=int,
            default=20,
            metavar='SIZE',
            help='Number of items per API request (default: 20)'
        )
        rest_group.add_argument(
            '--retry-attempts',
            type=int,
            default=3,
            metavar='COUNT',
            help='Number of retry attempts for failed requests (default: 3)'
        )
    
    @staticmethod
    def _get_examples(implementation_type: APIImplementationType) -> str:
        """Get usage examples for specific implementation."""
        impl_name = implementation_type.value.lower()
        base_cmd = f"python3 -m src.{impl_name}.{impl_name}_main"
        
        common_examples = f"""
Examples:
  # Fetch all data and export to enhanced CSV
  {base_cmd}
  
  # Fetch only characters
  {base_cmd} --characters-only
  
  # Fetch only locations  
  {base_cmd} --locations-only
  
  # Get statistics without exporting
  {base_cmd} --stats-only
  
  # Fetch specific character with location details
  {base_cmd} --character-id 1
  
  # Export to custom directory
  {base_cmd} --output-dir /custom/path
  
  # Verbose output
  {base_cmd} --verbose
"""
        
        if implementation_type == APIImplementationType.GRAPHQL:
            graphql_examples = f"""
  # GraphQL-specific examples:
  # Use optimized single query (demo, first page only)
  {base_cmd} --optimized
  
  # Use ultra-optimized combined queries (full dataset)
  {base_cmd} --ultra-optimized
  
  # Compare query complexity levels
  {base_cmd} --query-complexity ultra --stats-only
"""
            return common_examples + graphql_examples
        
        elif implementation_type == APIImplementationType.REST:
            rest_examples = f"""
  # REST-specific examples:
  # Custom batch size for pagination
  {base_cmd} --batch-size 50
  
  # Increase retry attempts for unreliable networks
  {base_cmd} --retry-attempts 5
"""
            return common_examples + rest_examples
        
        return common_examples
    
    @staticmethod
    def parse_and_validate(args: argparse.Namespace) -> Dict[str, Any]:
        """Parse and validate CLI arguments.
        
        Args:
            args: Parsed arguments from ArgumentParser
            
        Returns:
            Dictionary with validated and processed arguments
            
        Raises:
            ValueError: If arguments are invalid or conflicting
        """
        # Determine operation mode
        mode = CLIArgumentParser._determine_mode(args)
        
        # Validate argument combinations
        CLIArgumentParser._validate_arguments(args, mode)
        
        # Process and return configuration
        return {
            'mode': mode,
            'character_id': getattr(args, 'character_id', None),
            'characters_only': getattr(args, 'characters_only', False),
            'locations_only': getattr(args, 'locations_only', False),
            'stats_only': getattr(args, 'stats_only', False),
            'output_dir': getattr(args, 'output_dir', Config.OUTPUT_DIR),
            'format': getattr(args, 'format', 'enhanced'),
            'verbose': getattr(args, 'verbose', False),
            'quiet': getattr(args, 'quiet', False),
            'dry_run': getattr(args, 'dry_run', False),
            # GraphQL-specific
            'optimized': getattr(args, 'optimized', False),
            'ultra_optimized': getattr(args, 'ultra_optimized', False),
            'query_complexity': getattr(args, 'query_complexity', 'simple'),
            # REST-specific
            'batch_size': getattr(args, 'batch_size', 20),
            'retry_attempts': getattr(args, 'retry_attempts', 3),
        }
    
    @staticmethod
    def _determine_mode(args: argparse.Namespace) -> CLIMode:
        """Determine the operation mode from arguments."""
        if hasattr(args, 'character_id') and args.character_id:
            return CLIMode.SINGLE_CHARACTER
        elif getattr(args, 'stats_only', False):
            return CLIMode.STATISTICS_ONLY
        elif getattr(args, 'characters_only', False):
            return CLIMode.CHARACTERS_ONLY
        elif getattr(args, 'locations_only', False):
            return CLIMode.LOCATIONS_ONLY
        else:
            return CLIMode.FULL_EXPORT
    
    @staticmethod
    def _validate_arguments(args: argparse.Namespace, mode: CLIMode) -> None:
        """Validate argument combinations."""
        # Check for conflicting flags
        flags = [
            getattr(args, 'characters_only', False),
            getattr(args, 'locations_only', False),
            getattr(args, 'stats_only', False)
        ]
        
        if sum(flags) > 1:
            raise ValueError("Cannot specify multiple exclusive flags: --characters-only, --locations-only, --stats-only")
        
        # Validate character ID
        if hasattr(args, 'character_id') and args.character_id is not None:
            if args.character_id <= 0:
                raise ValueError("Character ID must be a positive integer")
        
        # Validate output directory
        output_dir = getattr(args, 'output_dir', Config.OUTPUT_DIR)
        if not output_dir:
            raise ValueError("Output directory cannot be empty")
        
        # Validate quiet/verbose combination
        if getattr(args, 'quiet', False) and getattr(args, 'verbose', False):
            raise ValueError("Cannot specify both --quiet and --verbose")
        
        # REST-specific validations
        if hasattr(args, 'batch_size') and args.batch_size <= 0:
            raise ValueError("Batch size must be a positive integer")
        
        if hasattr(args, 'retry_attempts') and args.retry_attempts < 0:
            raise ValueError("Retry attempts must be non-negative")
        
        # GraphQL-specific validations
        if hasattr(args, 'optimized') and hasattr(args, 'ultra_optimized'):
            if args.optimized and args.ultra_optimized:
                raise ValueError("Cannot specify both --optimized and --ultra-optimized")