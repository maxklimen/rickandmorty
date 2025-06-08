"""FastAPI application for Rick and Morty API client."""
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
from datetime import datetime

from ..rest.rest_client import RESTClient
from ..rest.rest_data_processor import RESTDataProcessor
from ..shared.csv_exporter import CSVExporter
from ..shared.config import Config
from ..shared.utils import setup_logging, APIError

logger = setup_logging(__name__)

app = FastAPI(
    title="Rick and Morty API Client",
    description="A dual REST/GraphQL client for the Rick and Morty API with CSV export capabilities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic models for API responses
class CharacterResponse(BaseModel):
    id: int
    name: str
    status: str
    species: str
    origin_name: str
    location_id: Optional[int]
    location_name: str
    image: str
    episode_count: int

class LocationResponse(BaseModel):
    id: int
    name: str
    type: str
    dimension: str
    resident_count: int

class ExportResponse(BaseModel):
    status: str
    message: str
    files: Dict[str, str]
    timestamp: str

class StatisticsResponse(BaseModel):
    total_characters: int
    total_locations: int
    character_status: Dict[str, int]
    character_species: Dict[str, int]
    location_types: Dict[str, int]
    most_populated_locations: List[Dict[str, Any]]

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    api_endpoints: Dict[str, str]

# Global client instances (consider using dependency injection for production)
rest_client = RESTClient()
data_processor = RESTDataProcessor()

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main web UI."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check and API information."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        api_endpoints={
            "rest": Config.REST_BASE_URL,
            "graphql": Config.GRAPHQL_URL
        }
    )

@app.get("/api/characters", response_model=List[CharacterResponse])
async def get_characters(
    status: Optional[str] = Query(None, description="Filter by status (Alive, Dead, unknown)"),
    species: Optional[str] = Query(None, description="Filter by species"),
    origin: Optional[str] = Query(None, description="Filter by origin name"),
    limit: int = Query(100, ge=1, le=826, description="Number of characters to return"),
    offset: int = Query(0, ge=0, description="Number of characters to skip")
):
    """Get all characters with optional filtering."""
    try:
        # Fetch all characters
        characters = rest_client.fetch_all_characters()
        
        # Apply filters
        if status or species or origin:
            characters = data_processor.filter_characters(
                characters, 
                status=status, 
                species=species, 
                origin_name=origin
            )
        
        # Apply pagination
        paginated = characters[offset:offset + limit]
        
        # Process and return
        return [CharacterResponse(**char.to_dict()) for char in paginated]
        
    except APIError as e:
        logger.error(f"API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/characters/{character_id}", response_model=Dict[str, Any])
async def get_character_detail(character_id: int):
    """Get detailed information about a specific character including location details."""
    try:
        result = rest_client.fetch_character_with_location(character_id)
        
        character = result['character']
        location = result['location']
        
        response = character.to_dict()
        if location:
            response['location_details'] = {
                'id': location.id,
                'name': location.name,
                'type': location.type,
                'dimension': location.dimension,
                'resident_count': len(location.residents)
            }
        else:
            response['location_details'] = None
        
        return response
        
    except APIError as e:
        if e.status_code == 404:
            raise HTTPException(status_code=404, detail="Character not found")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/locations", response_model=List[LocationResponse])
async def get_locations(
    type_filter: Optional[str] = Query(None, alias="type", description="Filter by location type"),
    dimension: Optional[str] = Query(None, description="Filter by dimension"),
    min_residents: Optional[int] = Query(None, ge=0, description="Minimum number of residents"),
    limit: int = Query(100, ge=1, le=126, description="Number of locations to return"),
    offset: int = Query(0, ge=0, description="Number of locations to skip")
):
    """Get all locations with optional filtering."""
    try:
        # Fetch all locations
        locations = rest_client.fetch_all_locations()
        
        # Apply filters
        if type_filter or dimension or min_residents is not None:
            locations = data_processor.filter_locations(
                locations,
                type_filter=type_filter,
                dimension=dimension,
                min_residents=min_residents
            )
        
        # Apply pagination
        paginated = locations[offset:offset + limit]
        
        # Process and return
        return [
            LocationResponse(
                id=loc.id,
                name=loc.name,
                type=loc.type,
                dimension=loc.dimension,
                resident_count=len(loc.residents)
            )
            for loc in paginated
        ]
        
    except APIError as e:
        logger.error(f"API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/statistics", response_model=StatisticsResponse)
async def get_statistics():
    """Get statistics about all characters and locations."""
    try:
        characters = rest_client.fetch_all_characters()
        locations = rest_client.fetch_all_locations()
        
        stats = data_processor.get_statistics(characters, locations)
        
        return StatisticsResponse(**stats)
        
    except APIError as e:
        logger.error(f"API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export", response_model=ExportResponse)
async def export_data(
    background_tasks: BackgroundTasks,
    include_characters: bool = True,
    include_locations: bool = True
):
    """Export data to CSV files."""
    try:
        files = {}
        
        if include_characters:
            logger.info("Exporting characters...")
            characters = rest_client.fetch_all_characters()
            char_file = CSVExporter.write_characters(characters)
            files['characters'] = char_file
        
        if include_locations:
            logger.info("Exporting locations...")
            locations = rest_client.fetch_all_locations()
            loc_file = CSVExporter.write_locations(locations)
            files['locations'] = loc_file
        
        return ExportResponse(
            status="success",
            message="Data exported successfully",
            files=files,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@app.get("/api/export/download/{file_type}")
async def download_csv(file_type: str):
    """Download exported CSV file."""
    if file_type == "characters":
        filepath = Config.get_character_csv_path()
    elif file_type == "locations":
        filepath = Config.get_location_csv_path()
    else:
        raise HTTPException(status_code=400, detail="Invalid file type. Use 'characters' or 'locations'")
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"{file_type} CSV not found. Please export first.")
    
    return FileResponse(
        filepath,
        media_type='text/csv',
        filename=f"rickandmorty_{file_type}.csv"
    )

@app.get("/api/config")
async def get_config():
    """Get current configuration."""
    return Config.to_dict()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)