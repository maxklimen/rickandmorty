"""Configuration settings for Rick and Morty API client."""
import os
from typing import Dict, Any

class Config:
    """Application configuration."""
    
    # API Endpoints
    REST_BASE_URL = "https://rickandmortyapi.com/api"
    GRAPHQL_URL = "https://rickandmortyapi.com/graphql"
    
    # API Settings
    TIMEOUT = 30  # seconds
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    RETRY_BACKOFF = 2  # exponential backoff multiplier
    
    # Pagination
    REST_PAGE_SIZE = 20  # Fixed by API
    
    # Output settings
    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "output")
    CHARACTERS_CSV = "characters.csv"
    LOCATIONS_CSV = "locations.csv"
    
    # CSV Headers - Enhanced with complex relationships
    CHARACTER_CSV_HEADERS = ["id", "name", "status", "species", "origin_name", "location_id", "location_name", "location_type", "location_dimension"]
    LOCATION_CSV_HEADERS = ["id", "name", "type", "dimension", "resident_count", "character_names"]
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Performance settings
    CHUNK_SIZE = 100  # Process data in chunks for memory efficiency
    
    # API Response settings
    ENABLE_PROGRESS = True
    
    @classmethod
    def get_character_csv_path(cls) -> str:
        """Get full path for characters CSV."""
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        return os.path.join(cls.OUTPUT_DIR, cls.CHARACTERS_CSV)
    
    @classmethod
    def get_location_csv_path(cls) -> str:
        """Get full path for locations CSV."""
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        return os.path.join(cls.OUTPUT_DIR, cls.LOCATIONS_CSV)
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Export configuration as dictionary for API responses."""
        return {
            "rest_base_url": cls.REST_BASE_URL,
            "graphql_url": cls.GRAPHQL_URL,
            "timeout": cls.TIMEOUT,
            "max_retries": cls.MAX_RETRIES,
            "output_dir": cls.OUTPUT_DIR
        }