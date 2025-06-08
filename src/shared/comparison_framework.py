"""Comprehensive comparison framework for REST vs GraphQL implementations.

This module provides detailed analysis and comparison of the two API implementations,
including performance characteristics, trade-offs, and limitations.
"""
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

from .base_client import BaseAPIClient, APIImplementationType
from .utils import setup_logging

logger = setup_logging(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics for API implementation."""
    total_time: float
    api_calls: int
    data_fetched: Dict[str, int]
    throughput: float  # items per second
    latency_per_call: float  # average time per API call

@dataclass
class ImplementationComparison:
    """Comparison data between implementations."""
    rest_metrics: PerformanceMetrics
    graphql_metrics: PerformanceMetrics
    winner: str
    improvement_percentage: float
    trade_offs: Dict[str, str]

class APIComparisonFramework:
    """Framework for comparing REST and GraphQL implementations."""
    
    def __init__(self):
        self.logger = setup_logging(__name__)
    
    def compare_implementations(
        self,
        rest_client: BaseAPIClient,
        graphql_client: BaseAPIClient,
        test_scenarios: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Compare both implementations across multiple scenarios.
        
        Args:
            rest_client: REST API client
            graphql_client: GraphQL API client
            test_scenarios: List of scenarios to test
            
        Returns:
            Comprehensive comparison results
        """
        if test_scenarios is None:
            test_scenarios = ['full_dataset', 'single_character', 'locations_only']
        
        results = {
            'scenarios': {},
            'overall_analysis': {},
            'recommendations': {}
        }
        
        for scenario in test_scenarios:
            self.logger.info(f"Testing scenario: {scenario}")
            results['scenarios'][scenario] = self._test_scenario(
                scenario, rest_client, graphql_client
            )
        
        # Generate overall analysis
        results['overall_analysis'] = self._generate_overall_analysis(results['scenarios'])
        results['recommendations'] = self._generate_recommendations(results['overall_analysis'])
        
        return results
    
    def _test_scenario(
        self, 
        scenario: str, 
        rest_client: BaseAPIClient, 
        graphql_client: BaseAPIClient
    ) -> Dict[str, Any]:
        """Test a specific scenario with both clients."""
        
        scenario_results = {
            'scenario': scenario,
            'rest_results': None,
            'graphql_results': None,
            'comparison': None
        }
        
        try:
            # Test REST implementation
            self.logger.info(f"Testing REST for scenario: {scenario}")
            scenario_results['rest_results'] = self._run_scenario_test(rest_client, scenario)
            
            # Test GraphQL implementation
            self.logger.info(f"Testing GraphQL for scenario: {scenario}")
            scenario_results['graphql_results'] = self._run_scenario_test(graphql_client, scenario)
            
            # Compare results
            scenario_results['comparison'] = self._compare_scenario_results(
                scenario_results['rest_results'],
                scenario_results['graphql_results']
            )
            
        except Exception as e:
            self.logger.error(f"Error testing scenario {scenario}: {e}")
            scenario_results['error'] = str(e)
        
        return scenario_results
    
    def _run_scenario_test(self, client: BaseAPIClient, scenario: str) -> PerformanceMetrics:
        """Run a specific test scenario with a client."""
        start_time = time.time()
        api_calls = 0
        data_fetched = {'characters': 0, 'locations': 0}
        
        try:
            if scenario == 'full_dataset':
                if hasattr(client, 'fetch_all_data_ultra_optimized'):
                    # Use GraphQL optimization if available
                    result = client.fetch_all_data_ultra_optimized()
                    data_fetched['characters'] = len(result.get('characters', []))
                    data_fetched['locations'] = len(result.get('locations', []))
                    api_calls = result.get('api_calls', client._estimate_api_calls())
                else:
                    # Standard approach
                    characters = client.fetch_all_characters()
                    locations = client.fetch_all_locations()
                    data_fetched['characters'] = len(characters)
                    data_fetched['locations'] = len(locations)
                    api_calls = client._estimate_api_calls()
                    
            elif scenario == 'single_character':
                result = client.fetch_character_with_location(1)
                data_fetched['characters'] = 1
                data_fetched['locations'] = 1 if result.get('location') else 0
                api_calls = 2  # Character + location fetch
                
            elif scenario == 'locations_only':
                locations = client.fetch_all_locations()
                data_fetched['locations'] = len(locations)
                api_calls = 7  # Estimated location pages
                
        except Exception as e:
            self.logger.error(f"Scenario test failed: {e}")
            raise
        
        total_time = time.time() - start_time
        total_items = data_fetched['characters'] + data_fetched['locations']
        
        return PerformanceMetrics(
            total_time=total_time,
            api_calls=api_calls,
            data_fetched=data_fetched,
            throughput=total_items / total_time if total_time > 0 else 0,
            latency_per_call=total_time / api_calls if api_calls > 0 else 0
        )
    
    def _compare_scenario_results(
        self, 
        rest_metrics: PerformanceMetrics, 
        graphql_metrics: PerformanceMetrics
    ) -> ImplementationComparison:
        """Compare metrics between REST and GraphQL."""
        
        # Determine winner based on total time
        if rest_metrics.total_time < graphql_metrics.total_time:
            winner = 'REST'
            improvement = ((graphql_metrics.total_time - rest_metrics.total_time) / graphql_metrics.total_time) * 100
        else:
            winner = 'GraphQL'
            improvement = ((rest_metrics.total_time - graphql_metrics.total_time) / rest_metrics.total_time) * 100
        
        # Analyze trade-offs
        trade_offs = {}
        
        if rest_metrics.api_calls != graphql_metrics.api_calls:
            if rest_metrics.api_calls > graphql_metrics.api_calls:
                trade_offs['api_calls'] = f"GraphQL uses {graphql_metrics.api_calls} calls vs REST's {rest_metrics.api_calls}"
            else:
                trade_offs['api_calls'] = f"REST uses {rest_metrics.api_calls} calls vs GraphQL's {graphql_metrics.api_calls}"
        
        if abs(rest_metrics.latency_per_call - graphql_metrics.latency_per_call) > 0.1:
            if rest_metrics.latency_per_call < graphql_metrics.latency_per_call:
                trade_offs['latency'] = "REST has lower per-call latency"
            else:
                trade_offs['latency'] = "GraphQL has lower per-call latency"
        
        return ImplementationComparison(
            rest_metrics=rest_metrics,
            graphql_metrics=graphql_metrics,
            winner=winner,
            improvement_percentage=improvement,
            trade_offs=trade_offs
        )
    
    def _generate_overall_analysis(self, scenarios: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall analysis from scenario results."""
        
        analysis = {
            'rest_advantages': [],
            'graphql_advantages': [],
            'performance_summary': {},
            'use_case_recommendations': {}
        }
        
        # Analyze wins per implementation
        rest_wins = 0
        graphql_wins = 0
        
        for scenario_name, scenario_data in scenarios.items():
            if 'comparison' in scenario_data and scenario_data['comparison']:
                comparison = scenario_data['comparison']
                if comparison.winner == 'REST':
                    rest_wins += 1
                else:
                    graphql_wins += 1
        
        # REST advantages
        analysis['rest_advantages'] = [
            "Simple, predictable request/response pattern",
            "Lower per-request latency",
            "Better HTTP caching support",
            "Easier debugging and monitoring",
            "Mature tooling ecosystem",
            "Stateless operations"
        ]
        
        # GraphQL advantages  
        analysis['graphql_advantages'] = [
            "Single endpoint for all operations",
            "Precise data fetching (no over/under-fetching)",
            "Strong type system and introspection",
            "Batch multiple operations in single request",
            "Real-time subscriptions support",
            "Client-driven API evolution"
        ]
        
        # Performance summary
        analysis['performance_summary'] = {
            'rest_scenarios_won': rest_wins,
            'graphql_scenarios_won': graphql_wins,
            'overall_winner': 'REST' if rest_wins > graphql_wins else 'GraphQL',
            'performance_notes': [
                "REST generally faster for simple, single-resource requests",
                "GraphQL can be faster for complex, multi-resource requests when optimized",
                "GraphQL query complexity directly impacts performance",
                "REST benefits from HTTP-level caching and CDNs"
            ]
        }
        
        # Use case recommendations
        analysis['use_case_recommendations'] = {
            'prefer_rest': [
                "Simple CRUD operations",
                "High-performance requirements with caching",
                "Mobile apps with bandwidth constraints",
                "APIs consumed by diverse third-party clients",
                "Teams new to API development"
            ],
            'prefer_graphql': [
                "Complex data relationships and joins",
                "Rapid frontend development with changing requirements",
                "Real-time applications needing subscriptions",
                "Internal APIs with coordinated frontend/backend teams",
                "Applications requiring precise data fetching"
            ]
        }
        
        return analysis
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate specific recommendations based on analysis."""
        
        return {
            'implementation_strategy': {
                'hybrid_approach': "Consider using both REST and GraphQL for different use cases",
                'migration_path': "Start with REST for MVP, evaluate GraphQL for complex features",
                'team_considerations': "Choose based on team expertise and project requirements"
            },
            'optimization_priorities': {
                'rest': [
                    "Implement response caching",
                    "Use HTTP/2 for multiplexing",
                    "Optimize pagination strategies",
                    "Add request batching where possible"
                ],
                'graphql': [
                    "Implement query complexity analysis",
                    "Use DataLoader for N+1 query prevention",
                    "Optimize resolver performance",
                    "Implement query caching and persisted queries"
                ]
            },
            'architectural_guidelines': {
                'rest': "Follow RESTful principles, use proper HTTP methods and status codes",
                'graphql': "Design schema carefully, avoid exposing internal data structures",
                'monitoring': "Implement proper metrics and alerting for both approaches",
                'security': "Apply rate limiting, authentication, and input validation"
            }
        }

class ImplementationAnalyzer:
    """Analyzer for detailed implementation characteristics."""
    
    @staticmethod
    def analyze_rest_characteristics() -> Dict[str, Any]:
        """Analyze REST implementation characteristics."""
        return {
            'architecture_pattern': 'Resource-based URLs with HTTP verbs',
            'data_fetching': 'Multiple requests for related data',
            'caching': 'HTTP-level caching (ETags, Cache-Control)',
            'type_safety': 'Depends on client implementation',
            'learning_curve': 'Low - familiar HTTP concepts',
            'tooling': 'Mature ecosystem (Postman, Swagger, etc.)',
            'bandwidth_usage': 'Can have over-fetching issues',
            'real_time': 'Requires additional protocols (SSE, WebSockets)',
            'versioning': 'URL-based or header-based versioning',
            'debugging': 'Standard HTTP debugging tools work well'
        }
    
    @staticmethod
    def analyze_graphql_characteristics() -> Dict[str, Any]:
        """Analyze GraphQL implementation characteristics."""
        return {
            'architecture_pattern': 'Single endpoint with flexible queries',
            'data_fetching': 'Precise fetching with single request',
            'caching': 'Query-level caching, more complex',
            'type_safety': 'Strong type system with schema',
            'learning_curve': 'Moderate - requires GraphQL knowledge',
            'tooling': 'Growing ecosystem (GraphiQL, Apollo, etc.)',
            'bandwidth_usage': 'Optimized - fetch only needed data',
            'real_time': 'Built-in subscription support',
            'versioning': 'Schema evolution without versioning',
            'debugging': 'Requires GraphQL-specific tools'
        }
    
    @staticmethod
    def get_implementation_limitations() -> Dict[str, List[str]]:
        """Get limitations of each implementation."""
        return {
            'rest_limitations': [
                "Multiple round trips for related data",
                "Over-fetching or under-fetching data",
                "Versioning complexity as API evolves",
                "Limited real-time capabilities",
                "Endpoint proliferation over time"
            ],
            'graphql_limitations': [
                "Query complexity can impact performance",
                "Caching is more complex than HTTP caching",
                "Potential for expensive queries if not monitored",
                "Learning curve for teams unfamiliar with GraphQL",
                "File uploads require additional protocols"
            ]
        }

def generate_comparison_report(
    rest_client: BaseAPIClient,
    graphql_client: BaseAPIClient,
    output_file: Optional[str] = None
) -> str:
    """Generate a comprehensive comparison report.
    
    Args:
        rest_client: REST API client instance
        graphql_client: GraphQL API client instance
        output_file: Optional file path to save the report
        
    Returns:
        Formatted comparison report as string
    """
    framework = APIComparisonFramework()
    analyzer = ImplementationAnalyzer()
    
    # Run comparison
    comparison_results = framework.compare_implementations(rest_client, graphql_client)
    
    # Get detailed characteristics
    rest_chars = analyzer.analyze_rest_characteristics()
    graphql_chars = analyzer.analyze_graphql_characteristics()
    limitations = analyzer.get_implementation_limitations()
    
    # Generate report
    report_lines = [
        "# Rick and Morty API Implementation Comparison Report",
        "",
        "## Executive Summary",
        "",
        f"This report compares REST and GraphQL implementations for the Rick and Morty API.",
        f"Overall performance winner: **{comparison_results['overall_analysis']['performance_summary']['overall_winner']}**",
        "",
        "## Performance Analysis",
        ""
    ]
    
    # Add scenario results
    for scenario_name, scenario_data in comparison_results['scenarios'].items():
        if 'comparison' in scenario_data and scenario_data['comparison']:
            comp = scenario_data['comparison']
            report_lines.extend([
                f"### {scenario_name.replace('_', ' ').title()} Scenario",
                f"- Winner: **{comp.winner}** ({comp.improvement_percentage:.1f}% faster)",
                f"- REST: {comp.rest_metrics.total_time:.2f}s, {comp.rest_metrics.api_calls} API calls",
                f"- GraphQL: {comp.graphql_metrics.total_time:.2f}s, {comp.graphql_metrics.api_calls} API calls",
                ""
            ])
    
    # Add advantages
    analysis = comparison_results['overall_analysis']
    report_lines.extend([
        "## Implementation Advantages",
        "",
        "### REST Advantages",
        ""
    ])
    
    for advantage in analysis['rest_advantages']:
        report_lines.append(f"- {advantage}")
    
    report_lines.extend([
        "",
        "### GraphQL Advantages",
        ""
    ])
    
    for advantage in analysis['graphql_advantages']:
        report_lines.append(f"- {advantage}")
    
    # Add limitations
    report_lines.extend([
        "",
        "## Limitations",
        "",
        "### REST Limitations",
        ""
    ])
    
    for limitation in limitations['rest_limitations']:
        report_lines.append(f"- {limitation}")
    
    report_lines.extend([
        "",
        "### GraphQL Limitations",
        ""
    ])
    
    for limitation in limitations['graphql_limitations']:
        report_lines.append(f"- {limitation}")
    
    # Add recommendations
    recs = comparison_results['recommendations']
    report_lines.extend([
        "",
        "## Recommendations",
        "",
        "### When to Use REST",
        ""
    ])
    
    for use_case in analysis['use_case_recommendations']['prefer_rest']:
        report_lines.append(f"- {use_case}")
    
    report_lines.extend([
        "",
        "### When to Use GraphQL",
        ""
    ])
    
    for use_case in analysis['use_case_recommendations']['prefer_graphql']:
        report_lines.append(f"- {use_case}")
    
    report_content = "\n".join(report_lines)
    
    # Save to file if requested
    if output_file:
        with open(output_file, 'w') as f:
            f.write(report_content)
        logger.info(f"Comparison report saved to {output_file}")
    
    return report_content