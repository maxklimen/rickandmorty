# Sample Output

This directory contains complete sample output from running the Rick and Morty API client, demonstrating the full dataset and output format.

## Files Included

### 📊 Data Files
- **`characters.csv`** - All 826 characters with enhanced fields
- **`locations.csv`** - All 126 locations with complete info

### 📋 Metadata
- **`execution_metadata.json`** - Complete execution statistics and data quality metrics
- **`README.md`** - This file explaining the sample output

## Dataset Overview

### Characters (826 total)
```csv
id,name,status,species,type,gender,origin.name,origin.id,location.name,location.id
1,Rick Sanchez,Alive,Human,,Male,Earth (C-137),1,Citadel of Ricks,3
2,Morty Smith,Alive,Human,,Male,unknown,,Citadel of Ricks,3
3,Summer Smith,Alive,Human,,Female,Earth (Replacement Dimension),20,Earth (Replacement Dimension),20
```

**Character Status Breakdown:**
- 439 Alive (53.1%)
- 287 Dead (34.7%) 
- 100 unknown (12.1%)

**Top Species:**
- Human: 366 (44.3%)
- Alien: 205 (24.8%)
- Humanoid: 68 (8.2%)

### Locations (126 total)
```csv
id,name,type,dimension
1,Earth (C-137),Planet,Dimension C-137
2,Abadango,Cluster,unknown
3,Citadel of Ricks,Space station,unknown
```

**Location Types:**
- Planet: 61 (48.4%)
- Space station: 12 (9.5%)
- Dimension: 8 (6.3%)
- Microverse: 7 (5.6%)

## Data Quality

### Completeness
- **97.5% of characters** have location IDs (805/826)
- **51.2% of characters** have origin IDs (423/826)
- **74.6% of locations** have residents (94/126)

### Missing Data Handling
- Characters without location URLs get blank `location.id`
- Characters with "unknown" origin get blank `origin.id`
- All characters have complete basic info (name, status, species)

## Execution Details

**Performance:**
- Total execution time: ~2.85 seconds
- API calls made: 49 (42 character pages + 7 location pages)
- No rate limiting encountered
- 0 retry attempts needed

**Generated:** June 9, 2024  
**API Version:** REST v1  
**Client Version:** Rick and Morty API Client v1.0

## Usage

These files demonstrate exactly what you'll get when running:
```bash
python main.py
```

The data is current as of the generation date and represents the complete Rick and Morty universe as available through the API.

## File Formats

Both CSV files use:
- UTF-8 encoding
- Standard CSV format (RFC 4180)
- Headers included
- Compatible with Excel, Google Sheets, pandas, etc.

## Data Analysis Ready

Example usage:
```python
import pandas as pd

# Load the data
characters = pd.read_csv('sample_output/characters.csv')
locations = pd.read_csv('sample_output/locations.csv')

# Analyze character migration
migrated = characters[characters['origin.id'] != characters['location.id']]
print(f"{len(migrated)} characters have moved from their origin")

# Most popular current locations
popular_locations = characters['location.name'].value_counts().head()
print("Most popular locations:")
print(popular_locations)
```