"""PreDB API Client - Handles PreDB.net API interactions."""

from datetime import datetime
import requests
import timeago
from typing import Optional, Dict, Any, List

class PreDBClient:
	"""
	PreDB API Client class
	"""

	API_URL = "https://api.predb.net/"

	# Status code mapping (class constant)
	STATUS_MAP = {
		1: "NUKED",
		2: "UNNUKED",
		3: "DELPRE",
		4: "UNDELPRE"
	}

	# Search type to API parameter mapping (class constant)
	TYPE_MAPPING = {
		'dupe': None,      # default search
		'search': None,    # default search
		'pre': 'pre',
		'nfo': 'nfo',
		'group': 'group',
		'section': 'section',
		'cat': 'section',      # alias for section
		'category': 'section', # alias for section
		'genre': 'genre',
		'tag': 'tag',
		'lang': 'tag',         # alias for tag
		'language': 'tag',     # alias for tag
		'status': 'status',
		'nuked': 'nuked',
		'unnuked': 'unnuked',
		'delpre': 'delpre',
		'undelpre': 'undelpre'
	}

	def __init__(self):
		"""Initialize client with empty search state"""
		self.search_query = ""
		self.search_type = ""

	def search(self, search: str, user_agent: str) -> Optional[Dict[str, Any]]:
		"""
		Main search function

		Args:
			search: Search query with optional command prefix (!type or /type)
			user_agent: Additional user agent string to append

		Returns:
			API response as dict or None if no search provided
		"""
		if not search:
			return None

		headers = {"User-Agent": f"predb-python-client v2.6.0/{user_agent}"}
		print(search)

		# Parse command and search type
		command = "/" if search.startswith("/") else "!"
		parts = search.split(maxsplit=1)
		search_type = parts[0].replace(command, "").lower()
		search_query = parts[1].strip() if len(parts) > 1 else ""

		# Store for later use
		self.search_type = search_type.capitalize()
		self.search_query = "Last releases" if search_type == "last" else search_query

		# Build API parameters
		params = {}
		if search_query:
			params['q'] = search_query

		# Add type parameter based on mapping
		if search_type in self.TYPE_MAPPING:
			api_type = self.TYPE_MAPPING[search_type]
			if api_type:
				params['type'] = api_type
		elif search_type != "last":
			# Fallback for unknown types
			params['type'] = search_type

		# Make API request with error handling
		try:
			response = requests.get(
				self.API_URL,
				params=params,
				headers=headers,
				timeout=10
			)
			response.raise_for_status()
			return response.json()
		except requests.exceptions.Timeout:
			return {"status": "error", "message": "Request timeout"}
		except requests.exceptions.RequestException as e:
			return {"status": "error", "message": str(e)}
		except ValueError as e:
			return {"status": "error", "message": "Invalid JSON response"}

	def format_as_text(self, results: Optional[Dict[str, Any]]) -> str:
		"""
		Format API results as text for display

		Args:
			results: API response dictionary

		Returns:
			Formatted string for display
		"""
		if not results:
			return "No results"

		if results.get("status") != "success":
			return f"Error: {results.get('message', 'Unknown error')}"

		if int(results.get("results", 0)) == 0:
			return "No releases found"

		formatted_releases = []

		for release in results.get("data", []):
			lines = self._format_release(release)
			formatted_releases.append("\n".join(lines))

		return "\n\n".join(formatted_releases)

	def _format_release(self, release: Dict[str, Any]) -> list:
		"""
		Format a single release entry

		Args:
			release: Release data dictionary

		Returns:
			List of formatted lines
		"""
		lines = [f"**Release:** {release['release']}"]

		# Format pretime
		try:
			pretime = datetime.fromtimestamp(int(release["pretime"]))
			time_ago = timeago.format(pretime, datetime.now())
			lines.append(
				f"**Pretime:** {pretime.strftime('%d/%m/%Y - %H:%M:%S')} / _{time_ago}_"
			)
		except (ValueError, KeyError):
			pass

		# Add optional fields
		field_mapping = [
			("Section", "section", None),
			("Group", "group", None),
			("Files", "files", lambda x: int(x) > 0),
			("Size", "size", lambda x: float(x) > 0),
			("Genre", "genre", None)
		]

		for label, key, condition in field_mapping:
			value = release.get(key)
			if value and (condition is None or condition(value)):
				lines.append(f"**{label}:** {value}")

		# Handle status if present
		status = int(release.get("status", 0))
		reason = release.get("reason")

		if status != 0 and reason:
			status_text = self.STATUS_MAP.get(status, f"STATUS_{status}")
			lines.append(f"**{status_text}:** _{reason}_")

		return lines
