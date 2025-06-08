"""Refactored REST API main entry point."""
import sys
import logging

from .rest_client_v2 import RESTClient
from ..shared.base_client import APIImplementationType
from ..shared.data_processor import DataProcessor
from ..shared.workflow_manager import APIWorkflowManager
from ..shared.argument_parser import CLIArgumentParser
from ..shared.utils import setup_logging
from ..shared.config import Config

def main():
    """Main entry point for REST implementation."""
    # Create argument parser for REST
    parser = CLIArgumentParser.create_parser(APIImplementationType.REST)
    args = parser.parse_args()
    
    try:
        # Parse and validate arguments
        config = CLIArgumentParser.parse_and_validate(args)
        
        # Update output directory if specified
        if config['output_dir'] != Config.OUTPUT_DIR:
            Config.OUTPUT_DIR = config['output_dir']
        
        # Create client and processor
        client = RESTClient()
        processor = DataProcessor()
        
        # Create and execute workflow
        workflow = APIWorkflowManager(client, processor)
        return workflow.execute_workflow(config)
        
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        logger = setup_logging(__name__)
        logger.error(f"Unexpected error in REST client: {str(e)}")
        if args.verbose if hasattr(args, 'verbose') else False:
            logger.exception("Full error details:")
        return 1

if __name__ == "__main__":
    sys.exit(main())