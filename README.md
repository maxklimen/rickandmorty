# 🚀 Rick and Morty API Client

> Get all Rick and Morty characters and locations in easy-to-use CSV files

## What This Does

This tool downloads all 826 characters and 126 locations from the Rick and Morty API and saves them as CSV files that you can open in Excel, Google Sheets, or use for data analysis.

### Key Features
- 📊 **Complete dataset**: All characters and locations
- 🔍 **Character lookup**: Get detailed info about any character
- 📁 **CSV export**: Ready for Excel, analysis tools
- 🚀 **Fast & reliable**: ~3 seconds to get everything
- 🛡️ **Error handling**: Won't crash on network issues

## 🚀 Quick Start

### 1. Install
```bash
# You need Python 3.7 or higher
pip install requests
```

### 2. Run
```bash
# Download everything to CSV files
python main.py
```

That's it! You'll get:
```
📁 output/
├── 📄 characters.csv    # All 826 characters
└── 📄 locations.csv     # All 126 locations
```

### 3. Optional Commands
```bash
# Look up a specific character (with location details)
python main.py --character-id 1

# Save to a different folder
python main.py --output-dir my_data
```

## 📊 What You Get

### characters.csv
Contains all 826 characters with these columns:

| Column | Example | Description |
|--------|---------|-------------|
| `id` | 1 | Character ID |
| `name` | Rick Sanchez | Character name |
| `status` | Alive | Alive, Dead, or unknown |
| `species` | Human | Character species |
| `type` | | Character variant (e.g., "Evil", "Cronenberg") |
| `gender` | Male | Character gender |
| `origin.name` | Earth (C-137) | Where they're from |
| `origin.id` | 1 | Origin location ID |
| `location.name` | Citadel of Ricks | Where they are now |
| `location.id` | 3 | Current location ID |

### locations.csv
Contains all 126 locations with these columns:

| Column | Example | Description |
|--------|---------|-------------|
| `id` | 1 | Location ID |
| `name` | Earth (C-137) | Location name |
| `type` | Planet | Type (Planet, Space station, etc.) |
| `dimension` | Dimension C-137 | Which dimension |

### Why Enhanced Fields?
- **Human readable**: Names you can understand
- **Machine readable**: IDs for databases/analysis
- **Consistent**: Both origin and current location have name + ID
- **Analysis ready**: Track character movement, demographics, etc.

## 🎯 Use Cases

### Data Analysis
- Character demographics by location
- Track character movement between dimensions
- Species distribution analysis
- Status statistics (alive/dead/unknown)

### Business Intelligence
- Most popular locations
- Character relationship networks
- Origin vs current location patterns

### Application Development
- Character lookup with location details
- Populate databases with complete Rick and Morty data
- Build Rick and Morty apps/games

## 🔗 Related Files

- **[TASK.md](TASK.md)** - Original requirements and specifications
- **[IMPLEMENTATION.md](IMPLEMENTATION.md)** - Technical details, API choices, and GraphQL assessment

## 📊 Sample Output

```csv
id,name,status,species,type,gender,origin.name,origin.id,location.name,location.id
1,Rick Sanchez,Alive,Human,,Male,Earth (C-137),1,Citadel of Ricks,3
2,Morty Smith,Alive,Human,,Male,unknown,,Citadel of Ricks,3
3,Summer Smith,Alive,Human,,Female,Earth (Replacement Dimension),20,Earth (Replacement Dimension),20
```

## 💡 Tips

- **Excel users**: Files open directly in Excel with proper column formatting
- **Data analysis**: Use `location.id` and `origin.id` for joining data
- **Character lookup**: Use `--character-id` to get detailed info about specific characters
- **Troubleshooting**: If network fails, just run again - it's safe to retry

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.