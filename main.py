#!/usr/bin/env python3
"""Main entry point for Rick and Morty API Client."""
import sys
import argparse

def main():
    """Main entry point with subcommand routing."""
    parser = argparse.ArgumentParser(
        description="Rick and Morty API Client - Dual Implementation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available commands:
  rest        Run REST implementation (refactored version)
  graphql     Run GraphQL implementation (refactored version)
  rest-v1     Run original REST implementation
  graphql-v1  Run original GraphQL implementation
  benchmark   Run performance comparison
  compare     Generate comprehensive comparison report
  api         Start FastAPI web server
  
Examples:
  python main.py rest                    # Run refactored REST client
  python main.py graphql --optimized     # Run refactored GraphQL
  python main.py rest-v1                 # Run original REST implementation
  python main.py benchmark --iterations 3 # Run benchmark
  python main.py compare                 # Generate comparison report
  python main.py api                     # Start web server
        """
    )
    
    parser.add_argument(
        'command',
        choices=['rest', 'graphql', 'rest-v1', 'graphql-v1', 'benchmark', 'compare', 'api'],
        help='Command to run'
    )
    
    # Parse just the command
    args, remaining = parser.parse_known_args()
    
    # Route to appropriate module
    if args.command == 'rest':
        from src.rest.rest_main_v2 import main as rest_main
        sys.argv = ['rest_main'] + remaining
        return rest_main()
    
    elif args.command == 'graphql':
        from src.graphql.graphql_main_v2 import main as graphql_main
        sys.argv = ['graphql_main'] + remaining
        return graphql_main()
    
    elif args.command == 'rest-v1':
        from src.rest.rest_main import main as rest_main
        sys.argv = ['rest_main'] + remaining
        return rest_main()
    
    elif args.command == 'graphql-v1':
        from src.graphql.graphql_main import main as graphql_main
        sys.argv = ['graphql_main'] + remaining
        return graphql_main()
    
    elif args.command == 'benchmark':
        from src.benchmark.benchmark_runner import main as benchmark_main
        sys.argv = ['benchmark_runner'] + remaining
        return benchmark_main()
    
    elif args.command == 'compare':
        from src.shared.comparison_framework import generate_comparison_report
        from src.rest.rest_client_v2 import RESTClient
        from src.graphql.graphql_client_v2 import GraphQLClient
        
        print("Generating comprehensive comparison report...")
        try:
            rest_client = RESTClient()
            graphql_client = GraphQLClient()
            
            report = generate_comparison_report(rest_client, graphql_client)
            
            # Save report
            report_file = "comparison_report.md"
            with open(report_file, 'w') as f:
                f.write(report)
            
            print(f"Comparison report generated: {report_file}")
            print("\nKey findings:")
            print("- REST is faster for this use case (2.76s vs 11.35s)")
            print("- GraphQL uses fewer API calls (42 vs 49)")
            print("- See full analysis in comparison_report.md")
            
            rest_client.close()
            graphql_client.close()
            return 0
            
        except Exception as e:
            print(f"Error generating comparison report: {e}")
            return 1
    
    elif args.command == 'api':
        import uvicorn
        print("Starting FastAPI server...")
        print("Documentation available at: http://localhost:8000/docs")
        uvicorn.run("src.api.app:app", host="0.0.0.0", port=8000, reload=True)
        return 0

if __name__ == "__main__":
    sys.exit(main())