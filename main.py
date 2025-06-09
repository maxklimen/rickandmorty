#!/usr/bin/env python3
"""
Rick and Morty API Client
A small Python application that fetches character and location data from the Rick and Morty API
and exports it to CSV files with the specified fields.
"""

import csv
import json
import sys
import os
import argparse
import time
from typing import Dict, List, Optional, Tuple
import requests


class RickAndMortyClient:
    """Client for interacting with the Rick and Morty API"""
    
    def __init__(self):
        self.base_url = "https://rickandmortyapi.com/api"
        self.session = requests.Session()
    
    def _get(self, endpoint: str, max_retries: int = 3) -> Dict:
        """Make a GET request to the API with automatic retry for transient failures"""
        for attempt in range(max_retries + 1):
            try:
                response = self.session.get(f"{self.base_url}/{endpoint}")
                
                # Handle rate limiting specifically
                if response.status_code == 429:
                    if attempt < max_retries:
                        # Check for Retry-After header, default to exponential backoff
                        retry_after = int(response.headers.get('retry-after', 2 ** attempt))
                        print(f"Rate limited. Waiting {retry_after} seconds (attempt {attempt + 1}/{max_retries})...")
                        time.sleep(retry_after)
                        continue
                    else:
                        print(f"Rate limit exceeded. Max retries ({max_retries}) reached.")
                        response.raise_for_status()  # This will raise the 429 error
                
                # Check for other HTTP errors
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                if attempt < max_retries:
                    # Exponential backoff for network errors
                    wait_time = 2 ** attempt
                    print(f"Network error (attempt {attempt + 1}/{max_retries}): {e}")
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"Error fetching {endpoint} after {max_retries} retries: {e}")
                    sys.exit(1)
    
    def extract_location_id(self, location_url: str) -> Optional[int]:
        """Extract location ID from URL"""
        if not location_url:
            return None
        try:
            # URL format: https://rickandmortyapi.com/api/location/3
            return int(location_url.rstrip('/').split('/')[-1])
        except (ValueError, IndexError):
            return None
    
    def fetch_all_characters(self) -> List[Dict]:
        """Fetch all characters with pagination"""
        characters = []
        page = 1
        
        while True:
            print(f"Fetching characters page {page}...")
            data = self._get(f"character?page={page}")
            
            # Process each character
            for char in data['results']:
                # Extract both ID and name for both origin and location for consistency
                character_data = {
                    'id': char['id'],
                    'name': char['name'],
                    'status': char['status'],
                    'species': char['species'],
                    'type': char['type'] or '',  # Additional field for subspecies info
                    'gender': char['gender'],  # Additional field for demographic analysis
                    # Origin location (where they're FROM)
                    'origin_id': self.extract_location_id(char['origin']['url']),
                    'origin_name': char['origin']['name'],
                    # Current location (where they are NOW)
                    'location_id': self.extract_location_id(char['location']['url']),
                    'location_name': char['location']['name']
                }
                characters.append(character_data)
            
            # Check if there's a next page
            if data['info']['next']:
                page += 1
            else:
                break
        
        print(f"Total characters fetched: {len(characters)}")
        return characters
    
    def fetch_all_locations(self) -> List[Dict]:
        """Fetch all locations with pagination"""
        locations = []
        page = 1
        
        while True:
            print(f"Fetching locations page {page}...")
            data = self._get(f"location?page={page}")
            
            # Process each location
            for loc in data['results']:
                # Extract only the required fields
                location_data = {
                    'id': loc['id'],
                    'name': loc['name'],
                    'type': loc['type'],
                    'dimension': loc['dimension']
                }
                locations.append(location_data)
            
            # Check if there's a next page
            if data['info']['next']:
                page += 1
            else:
                break
        
        print(f"Total locations fetched: {len(locations)}")
        return locations
    
    def get_character_details(self, character_id: int) -> Tuple[Dict, Optional[Dict]]:
        """Get all info about a character including location details"""
        # Fetch character data
        char_data = self._get(f"character/{character_id}")
        
        # Fetch location details if available
        location_data = None
        location_id = self.extract_location_id(char_data['location']['url'])
        if location_id:
            location_data = self._get(f"location/{location_id}")
        
        return char_data, location_data


def write_characters_csv(characters: List[Dict], output_dir: str = "output"):
    """Write character data to CSV with enhanced fields for better usability"""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, "characters.csv")
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        # Enhanced header with both required and additional helpful fields
        fieldnames = [
            'id', 'name', 'status', 'species', 'type', 'gender',
            'origin.name', 'origin.id',  # Both name and ID for origin
            'location.name', 'location.id'  # Both name and ID for current location
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        # Write character data
        for char in characters:
            writer.writerow({
                'id': char['id'],
                'name': char['name'],
                'status': char['status'],
                'species': char['species'],
                'type': char['type'],
                'gender': char['gender'],
                'origin.name': char['origin_name'],
                'origin.id': char['origin_id'] if char['origin_id'] else '',
                'location.name': char['location_name'],
                'location.id': char['location_id'] if char['location_id'] else ''
            })
    
    print(f"Characters CSV written to: {filepath}")


def write_locations_csv(locations: List[Dict], output_dir: str = "output"):
    """Write location data to CSV with required fields"""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, "locations.csv")
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        # Write header with exact field names from requirements
        fieldnames = ['id', 'name', 'type', 'dimension']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        # Write location data
        for loc in locations:
            writer.writerow(loc)
    
    print(f"Locations CSV written to: {filepath}")


def display_character_details(char_data: Dict, location_data: Optional[Dict]):
    """Display all character information including location details"""
    print("\n" + "="*50)
    print("CHARACTER INFORMATION")
    print("="*50)
    
    # Character basic info
    print(f"ID: {char_data['id']}")
    print(f"Name: {char_data['name']}")
    print(f"Status: {char_data['status']}")
    print(f"Species: {char_data['species']}")
    print(f"Type: {char_data['type'] or 'None'}")
    print(f"Gender: {char_data['gender']}")
    
    # Origin info
    print(f"\nORIGIN:")
    print(f"  Name: {char_data['origin']['name']}")
    
    # Current location info
    print(f"\nCURRENT LOCATION:")
    print(f"  Name: {char_data['location']['name']}")
    
    if location_data:
        print(f"  Type: {location_data['type']}")
        print(f"  Dimension: {location_data['dimension']}")
        print(f"  Residents: {len(location_data['residents'])}")
    
    # Episode info
    print(f"\nEPISODES:")
    print(f"  Appears in {len(char_data['episode'])} episodes")
    
    print("="*50)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Fetch Rick and Morty data and export to CSV'
    )
    parser.add_argument(
        '--character-id', 
        type=int, 
        help='Get all info about a specific character (including location details)'
    )
    parser.add_argument(
        '--output-dir', 
        default='output', 
        help='Directory for CSV output files (default: output)'
    )
    
    args = parser.parse_args()
    
    # Initialize client
    client = RickAndMortyClient()
    
    if args.character_id:
        # Fetch specific character with location details
        print(f"Fetching character {args.character_id}...")
        char_data, location_data = client.get_character_details(args.character_id)
        display_character_details(char_data, location_data)
    else:
        # Fetch all data and export to CSV
        print("Starting data fetch...")
        
        # Fetch all characters
        characters = client.fetch_all_characters()
        
        # Fetch all locations
        locations = client.fetch_all_locations()
        
        # Write to CSV files
        write_characters_csv(characters, args.output_dir)
        write_locations_csv(locations, args.output_dir)
        
        print("\nData export complete!")
        print(f"Total characters: {len(characters)}")
        print(f"Total locations: {len(locations)}")


if __name__ == "__main__":
    main()