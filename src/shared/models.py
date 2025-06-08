"""Data models for Rick and Morty API."""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class Origin:
    """Character origin location."""
    name: str
    url: Optional[str] = None

@dataclass
class Location:
    """Location model."""
    id: int
    name: str
    type: str
    dimension: str
    url: Optional[str] = None
    residents: List[str] = field(default_factory=list)
    created: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Location':
        """Create Location from API response."""
        return cls(
            id=data.get('id', 0),
            name=data.get('name', ''),
            type=data.get('type', ''),
            dimension=data.get('dimension', ''),
            url=data.get('url', ''),
            residents=data.get('residents', []),
            created=data.get('created', '')
        )
    
    def to_csv_row(self, character_names: Optional[List[str]] = None) -> List[str]:
        """Convert to CSV row format with enhanced resident details."""
        resident_count = len(self.residents)
        
        # Join character names with semicolon to handle commas in names
        character_names_str = ''
        if character_names:
            character_names_str = '; '.join(character_names)
        
        return [
            str(self.id),
            self.name,
            self.type,
            self.dimension,
            str(resident_count),
            character_names_str
        ]

@dataclass
class Character:
    """Character model."""
    id: int
    name: str
    status: str
    species: str
    type: str
    gender: str
    origin: Origin
    location: Dict[str, Any]
    image: str
    episode: List[str] = field(default_factory=list)
    url: Optional[str] = None
    created: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Character':
        """Create Character from API response."""
        origin_data = data.get('origin', {})
        origin = Origin(
            name=origin_data.get('name', ''),
            url=origin_data.get('url', '')
        )
        
        return cls(
            id=data.get('id', 0),
            name=data.get('name', ''),
            status=data.get('status', ''),
            species=data.get('species', ''),
            type=data.get('type', ''),
            gender=data.get('gender', ''),
            origin=origin,
            location=data.get('location', {}),
            image=data.get('image', ''),
            episode=data.get('episode', []),
            url=data.get('url', ''),
            created=data.get('created', '')
        )
    
    def get_location_id(self) -> Optional[int]:
        """Extract location ID from location URL."""
        if self.location and 'url' in self.location:
            url = self.location['url']
            if url and '/location/' in url:
                try:
                    return int(url.split('/location/')[-1])
                except (ValueError, IndexError):
                    return None
        return None
    
    def to_csv_row(self, location_details: Optional[Dict[str, Any]] = None) -> List[str]:
        """Convert to CSV row format with enhanced location details."""
        location_id = self.get_location_id()
        
        # Extract location details if provided
        location_name = self.location.get('name', '') if self.location else ''
        location_type = ''
        location_dimension = ''
        
        if location_details:
            location_name = location_details.get('name', location_name)
            location_type = location_details.get('type', '')
            location_dimension = location_details.get('dimension', '')
        
        return [
            str(self.id),
            self.name,
            self.status,
            self.species,
            self.origin.name,
            str(location_id) if location_id else '',
            location_name,
            location_type,
            location_dimension
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'species': self.species,
            'origin_name': self.origin.name,
            'location_id': self.get_location_id(),
            'location_name': self.location.get('name', ''),
            'image': self.image,
            'episode_count': len(self.episode)
        }

@dataclass
class PaginationInfo:
    """Pagination information."""
    count: int
    pages: int
    next: Optional[str] = None
    prev: Optional[str] = None

@dataclass
class APIResponse:
    """Generic API response wrapper."""
    data: List[Any]
    info: Optional[PaginationInfo] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def success(self) -> bool:
        """Check if response was successful."""
        return self.error is None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            'success': self.success,
            'data': self.data,
            'error': self.error,
            'timestamp': self.timestamp.isoformat()
        }