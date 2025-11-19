# __PreDB Python Client 🎉__

![Made with Python](https://img.shields.io/static/v1?label&message=Python&color=4B8BBE&logo=python&logoColor=FFD43B)

## __Python client for the [PreDB.net](https://predb.net) API.__

_Like it? I'd appreciate the support :)_

[![Watch on Twitch](https://img.shields.io/static/v1?label=Watch%20on&message=Twitch&color=bf94ff&logo=twitch&logoColor=fff)](https://propz.de/twitch/)
[![Join on Discord](https://img.shields.io/static/v1?label=Join%20on&message=Discord&color=7289da&logo=discord&logoColor=fff)](https://propz.de/discord/)
[![Donate on Ko-Fi](https://img.shields.io/static/v1?label=Donate%20on&message=Ko-Fi&color=ff5f5f&logo=kofi&logoColor=fff)](https://propz.de/kofi/)

## __Installation__

```bash
pip install predb
```

## __Usage__

```python
from predb import PreDBClient

# Initialize the client
client = PreDBClient()

# Search for releases
response = client.search("!search Ubuntu", user_agent="MyApp/1.0")

# Check the response
if response and response.get("status") == "success":
    for row in response.get("data", {}).get("rows", []):
        print(f"{row['name']} - {row['cat']}")
```

## __Search Types__

The client supports different search types using the command prefix format:

- `!search <query>` or `!dupe <query>` - General search
- `!pre <name>` - Search by exact release name
- `!nfo <query>` - Search in NFO files
- `!group <name>` - Search by group name
- `!section <name>` or `!cat <name>` - Search by section/category
- `!genre <name>` - Search by genre
- `!tag <name>` or `!lang <name>` - Search by tag/language
- `!nuked`, `!unnuked`, `!delpre`, `!undelpre` - Filter by status
- `!last` - Get last releases

## __Example__

```python
from predb import PreDBClient

client = PreDBClient()

# Search for a specific release
result = client.search("!pre Some.Release.Name-GRP", user_agent="MyApp/1.0")

# Search by group
result = client.search("!group RARBG", user_agent="MyApp/1.0")

# Get latest releases
result = client.search("!last", user_agent="MyApp/1.0")
```

## __API Response__

The API returns a dictionary with the following structure:

```python
{
    "status": "success",
    "message": "",
    "data": {
        "offset": 0,
        "total": 100,
        "time": 0.5,
        "rows": [
            {
                "id": "12345",
                "name": "Release.Name-GRP",
                "team": "GRP",
                "cat": "TV",
                "genre": "...",
                "url": "...",
                "size": "...",
                "files": "...",
                "pretime": 1234567890,
                "nuke": "...",
                "unnuke": "...",
                "reason": "...",
                ...
            }
        ]
    }
}
```

## Requirements

- Python 3.7+
- requests
- timeago

## License

MIT

_That's it!_

___Be excellent to each other. And, Party on, dudes!___
