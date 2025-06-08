"""Tests for CSV export functionality."""
import pytest
import os
import csv
import tempfile
from src.shared.csv_exporter import CSVExporter
from src.shared.models import Character, Location, Origin

class TestCSVExporter:
    """Test CSV export functionality."""
    
    @pytest.fixture
    def sample_characters(self):
        """Create sample characters for testing."""
        return [
            Character(
                id=1,
                name='Rick Sanchez',
                status='Alive',
                species='Human',
                type='',
                gender='Male',
                origin=Origin(name='Earth (C-137)'),
                location={'name': 'Citadel of Ricks', 'url': 'https://rickandmortyapi.com/api/location/3'},
                image='',
                episode=[]
            ),
            Character(
                id=2,
                name='Morty Smith',
                status='Alive',
                species='Human',
                type='',
                gender='Male',
                origin=Origin(name='unknown'),
                location={'name': 'Citadel of Ricks', 'url': 'https://rickandmortyapi.com/api/location/3'},
                image='',
                episode=[]
            )
        ]
    
    @pytest.fixture
    def sample_locations(self):
        """Create sample locations for testing."""
        return [
            Location(
                id=1,
                name='Earth (C-137)',
                type='Planet',
                dimension='Dimension C-137',
                residents=['url1', 'url2']
            ),
            Location(
                id=3,
                name='Citadel of Ricks',
                type='Space station',
                dimension='unknown',
                residents=['url1', 'url2', 'url3']
            )
        ]
    
    def test_write_characters(self, sample_characters, tmp_path):
        """Test writing characters to CSV."""
        filepath = tmp_path / "test_characters.csv"
        
        result = CSVExporter.write_characters(sample_characters, str(filepath))
        
        assert result == str(filepath)
        assert os.path.exists(filepath)
        
        # Verify content
        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            
            assert len(rows) == 3  # header + 2 characters
            assert rows[0] == ['id', 'name', 'status', 'species', 'origin_name', 'location_id']
            assert rows[1] == ['1', 'Rick Sanchez', 'Alive', 'Human', 'Earth (C-137)', '3']
            assert rows[2] == ['2', 'Morty Smith', 'Alive', 'Human', 'unknown', '3']
    
    def test_write_locations(self, sample_locations, tmp_path):
        """Test writing locations to CSV."""
        filepath = tmp_path / "test_locations.csv"
        
        result = CSVExporter.write_locations(sample_locations, str(filepath))
        
        assert result == str(filepath)
        assert os.path.exists(filepath)
        
        # Verify content
        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            
            assert len(rows) == 3  # header + 2 locations
            assert rows[0] == ['id', 'name', 'type', 'dimension']
            assert rows[1] == ['1', 'Earth (C-137)', 'Planet', 'Dimension C-137']
            assert rows[2] == ['3', 'Citadel of Ricks', 'Space station', 'unknown']
    
    def test_validate_csv_files(self, sample_characters, sample_locations, tmp_path):
        """Test CSV file validation."""
        # Create test directory structure
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        # Write test files
        char_file = output_dir / "characters.csv"
        loc_file = output_dir / "locations.csv"
        
        CSVExporter.write_characters(sample_characters, str(char_file))
        CSVExporter.write_locations(sample_locations, str(loc_file))
        
        # Mock config to use test directory
        import src.shared.config as config
        original_char_path = config.Config.get_character_csv_path
        original_loc_path = config.Config.get_location_csv_path
        
        config.Config.get_character_csv_path = lambda: str(char_file)
        config.Config.get_location_csv_path = lambda: str(loc_file)
        
        try:
            validation = CSVExporter.validate_csv_files()
            
            assert validation['valid'] is True
            assert validation['characters']['exists'] is True
            assert validation['characters']['row_count'] == 2
            assert validation['locations']['exists'] is True
            assert validation['locations']['row_count'] == 2
        finally:
            # Restore original methods
            config.Config.get_character_csv_path = original_char_path
            config.Config.get_location_csv_path = original_loc_path