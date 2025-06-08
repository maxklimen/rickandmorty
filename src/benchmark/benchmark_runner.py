"""Runner script for performance benchmarks."""
import argparse
import sys
import logging

from .performance_comparison import PerformanceComparison
from ..shared.utils import setup_logging

logger = setup_logging(__name__)

def main():
    """Main entry point for benchmark runner."""
    parser = argparse.ArgumentParser(
        description="Rick and Morty API Performance Benchmark",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run basic comparison (1 iteration each)
  python -m src.benchmark.benchmark_runner
  
  # Run with multiple iterations for more accurate results
  python -m src.benchmark.benchmark_runner --iterations 3
  
  # Skip optimized GraphQL demo
  python -m src.benchmark.benchmark_runner --no-optimized
  
  # Save results to specific file
  python -m src.benchmark.benchmark_runner --output results.json
        """
    )
    
    parser.add_argument(
        '--iterations', 
        type=int,
        default=1,
        help='Number of iterations for each benchmark (default: 1)'
    )
    parser.add_argument(
        '--no-optimized', 
        action='store_true',
        help='Skip optimized GraphQL benchmark'
    )
    parser.add_argument(
        '--output', 
        type=str,
        help='Output file for benchmark results'
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
    
    try:
        # Create and run comparison
        comparison = PerformanceComparison()
        
        print("Starting Rick and Morty API Performance Benchmark...")
        print(f"Iterations: {args.iterations}")
        print(f"Include Optimized: {not args.no_optimized}")
        print("-" * 60)
        
        # Run benchmarks
        results = comparison.run_comparison(
            iterations=args.iterations,
            include_optimized=not args.no_optimized
        )
        
        # Print summary
        comparison.print_summary()
        
        # Save results
        output_file = comparison.save_results(args.output)
        print(f"\nDetailed results saved to: {output_file}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Benchmark failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())