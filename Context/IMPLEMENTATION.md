# Rick and Morty API - Dual Implementation Context for Claude Code

## Project Overview

**Objective**: Build Python application demonstrating both REST and GraphQL API consumption patterns  
**Target**: Inscribe AI Customer Engineer exercise showcasing technical depth and customer optimization thinking  
**Deliverable**: Two implementations with performance comparison and customer-ready documentation

## Implementation Strategy

### Dual Approach Rationale
- **REST Implementation**: Meets explicit exercise requirements, shows traditional API handling
- **GraphQL Enhancement**: Demonstrates performance optimization (96% fewer API calls), modern API patterns
- **Customer Value**: Shows ability to deliver requirements while providing strategic optimization insights

## Technical Specifications

### REST API Details
- **Base URL**: `https://rickandmortyapi.com/api`
- **Characters**: `/character` (826 total, 20 per page = 42 pages)
- **Locations**: `/location` (126 total, 20 per page = 7 pages)
- **Total API Calls**: 49 (42 + 7)

### GraphQL API Details  
- **Endpoint**: `https://rickandmortyapi.com/graphql`
- **Characters + Locations**: 2 queries total
- **Performance Gain**: 96% reduction in API calls (49 → 2)

### Response Data Structures

#### Character Object (REST)
```json
{
  "id": 1,
  "name": "Rick Sanchez",
  "status": "Alive",
  "species": "Human",
  "origin": {"name": "Earth (C-137)", "url": "..."},
  "location": {"name": "Citadel of Ricks", "url": "..."}
}
```

#### GraphQL Character Query
```graphql
query GetCharacters($page: Int!) {
  characters(page: $page) {
    info { count pages next prev }
    results {
      id name status species
      origin { name }
      location { id name }
    }
  }
}
```

## Project Structure

### Dual Implementation Architecture
```
rick_morty_api/
├── src/
│   ├── rest/
│   │   ├── rest_client.py           # REST API client with pagination
│   │   ├── rest_data_processor.py   # REST response transformation
│   │   └── rest_main.py             # REST CLI entry point
│   ├── graphql/
│   │   ├── graphql_client.py        # GraphQL query client
│   │   ├── graphql_data_processor.py # GraphQL response transformation
│   │   └── graphql_main.py          # GraphQL CLI entry point
│   ├── shared/
│   │   ├── csv_exporter.py          # Shared CSV generation
│   │   ├── config.py                # API endpoints and constants
│   │   ├── models.py                # Data models/classes
│   │   └── utils.py                 # Shared utilities
│   └── benchmark/
│       ├── performance_comparison.py # Compare both approaches
│       └── benchmark_runner.py       # Performance testing
├── tests/
│   ├── test_rest_client.py
│   ├── test_graphql_client.py
│   └── test_csv_export.py
├── output/
│   ├── characters.csv               # Required output
│   └── locations.csv                # Required output
├── requirements.txt
├── README.md                        # Customer-facing documentation
└── PERFORMANCE.md                   # Benchmarks and recommendations
```

## Required CSV Outputs

### Characters CSV Fields
- `id`, `name`, `status`, `species`, `origin.name`, `location id`

### Locations CSV Fields  
- `id`, `name`, `type`, `dimension`

## Core Implementation Requirements

### REST Client Features
- Handle pagination through all 49 API calls
- Extract location ID from character location URLs
- Robust error handling for network failures
- Memory-efficient processing (don't hold all data in memory)
- Progress indicators for long-running operations

### GraphQL Client Features
- Schema introspection and validation
- Efficient nested queries for character + location data
- Variable handling for pagination
- Partial failure handling (GraphQL errors + data)
- Query optimization for minimal data transfer

### Shared Components
- CSV export with proper headers and formatting
- Configuration management
- Logging and error reporting
- Data validation and transformation
- Performance metrics collection

## Error Handling Patterns

### REST Error Scenarios
```python
# Network failures, timeouts
# HTTP status codes (404, 400, 500)
# Rate limiting responses
# Malformed JSON
# Pagination boundary conditions
```

### GraphQL Error Scenarios
```python
# GraphQL syntax errors
# Field validation errors  
# Partial query failures
# Network issues (same as REST)
# Schema mismatches
```

## Performance Requirements

### Benchmarking Targets
- **REST Implementation**: Complete in <30 seconds
- **GraphQL Implementation**: Complete in <5 seconds  
- **Memory Usage**: Process data in chunks, not all at once
- **Error Recovery**: Retry failed requests with exponential backoff

### Metrics to Collect
- Total execution time
- Number of API calls made
- Total data transferred
- Memory usage peaks
- Error rates and recovery success

## Customer Engineer Documentation

### README Structure
```markdown
# Rick and Morty API Client - Dual Implementation

## Quick Start
- REST approach (traditional)
- GraphQL approach (optimized)

## Performance Comparison
- API calls: 49 vs 2 (96% reduction)
- Execution time: ~15s vs ~3s
- Data transfer: [actual measurements]

## Implementation Choice Guide
- Use REST for: Learning, legacy system integration
- Use GraphQL for: Production systems, performance-critical applications

## Setup and Usage
[Clear installation and run instructions]
```

### Technical Recommendations Document
- When to choose each approach
- Performance characteristics
- Scalability considerations
- Error handling patterns
- Production deployment guidance

## Dependencies

### Core Libraries
```python
# REST implementation
requests>=2.31.0
urllib3>=2.0.0

# GraphQL implementation  
gql>=3.4.1
requests-toolbelt>=1.0.0

# Shared dependencies
csv (built-in)
json (built-in)
logging (built-in)
argparse (built-in)
time (built-in)

# Optional
pytest>=7.4.0  # for testing
rich>=13.0.0    # for pretty CLI output
```

## Success Criteria

### Functional Requirements
- [ ] All 826 characters exported correctly
- [ ] All 126 locations exported correctly
- [ ] Both implementations produce identical CSV outputs
- [ ] Error handling prevents data corruption
- [ ] Performance benchmarks demonstrate GraphQL advantages

### Code Quality
- [ ] Modular, maintainable architecture
- [ ] Comprehensive error handling
- [ ] Clear separation of concerns
- [ ] Production-ready logging
- [ ] Type hints and documentation

### Customer Engineer Value
- [ ] Clear performance comparison with real metrics
- [ ] Professional documentation suitable for customer presentation
- [ ] Technical recommendations with business context
- [ ] Demonstrates optimization thinking beyond basic requirements

## Next Steps for Claude Code Development

1. **Start with REST implementation** (meets core requirements)
2. **Add GraphQL implementation** (demonstrates optimization)
3. **Implement performance benchmarking** (quantify improvements)
4. **Create customer-ready documentation** (showcase consulting skills)
5. **Add comprehensive error handling** (production readiness)

Focus on creating working solutions first, then optimize for performance and documentation quality.