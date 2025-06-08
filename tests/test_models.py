"""Tests for data models."""
import pytest
from src.shared.models import Character, Location, Origin

class TestCharacterModel:
    """Test Character model functionality."""
    
    def test_character_from_dict(self):
        """Test creating character from API response."""
        data = {
            'id': 1,
            'name': 'Rick Sanchez',
            'status': 'Alive',
            'species': 'Human',
            'type': '',
            'gender': 'Male',
            'origin': {
                'name': 'Earth (C-137)',
                'url': 'https://rickandmortyapi.com/api/location/1'
            },
            'location': {
                'name': 'Citadel of Ricks',
                'url': 'https://rickandmortyapi.com/api/location/3'
            },
            'image': 'https://rickandmortyapi.com/api/character/avatar/1.jpeg',
            'episode': ['https://rickandmortyapi.com/api/episode/1'],
            'created': '2017-11-04T18:48:46.250Z'
        }
        
        character = Character.from_dict(data)
        
        assert character.id == 1
        assert character.name == 'Rick Sanchez'
        assert character.status == 'Alive'
        assert character.species == 'Human'
        assert character.origin.name == 'Earth (C-137)'
        assert character.location['name'] == 'Citadel of Ricks'
    
    def test_get_location_id(self):
        """Test extracting location ID from URL."""
        character = Character(
            id=1,
            name='Test',
            status='Alive',
            species='Human',
            type='',
            gender='Male',
            origin=Origin(name='Earth'),
            location={'url': 'https://rickandmortyapi.com/api/location/3'},
            image='',
            episode=[]
        )
        
        assert character.get_location_id() == 3
    
    def test_get_location_id_no_url(self):
        """Test location ID extraction with missing URL."""
        character = Character(
            id=1,
            name='Test',
            status='Alive',
            species='Human',
            type='',
            gender='Male',
            origin=Origin(name='Earth'),
            location={},
            image='',
            episode=[]
        )
        
        assert character.get_location_id() is None
    
    def test_to_csv_row(self):
        """Test CSV row generation."""
        character = Character(
            id=1,
            name='Rick Sanchez',
            status='Alive',
            species='Human',
            type='',
            gender='Male',
            origin=Origin(name='Earth (C-137)'),
            location={
                'name': 'Citadel of Ricks',
                'url': 'https://rickandmortyapi.com/api/location/3'
            },
            image='',
            episode=[]
        )
        
        row = character.to_csv_row()
        assert row == ['1', 'Rick Sanchez', 'Alive', 'Human', 'Earth (C-137)', '3']

class TestLocationModel:
    """Test Location model functionality."""
    
    def test_location_from_dict(self):
        """Test creating location from API response."""
        data = {
            'id': 1,
            'name': 'Earth (C-137)',
            'type': 'Planet',
            'dimension': 'Dimension C-137',
            'residents': [
                'https://rickandmortyapi.com/api/character/38',
                'https://rickandmortyapi.com/api/character/45'
            ],
            'created': '2017-11-10T12:42:04.162Z'
        }
        
        location = Location.from_dict(data)
        
        assert location.id == 1
        assert location.name == 'Earth (C-137)'
        assert location.type == 'Planet'
        assert location.dimension == 'Dimension C-137'
        assert len(location.residents) == 2
    
    def test_to_csv_row(self):
        """Test CSV row generation."""
        location = Location(
            id=1,
            name='Earth (C-137)',
            type='Planet',
            dimension='Dimension C-137',
            residents=['url1', 'url2']
        )
        
        row = location.to_csv_row()
        assert row == ['1', 'Earth (C-137)', 'Planet', 'Dimension C-137']