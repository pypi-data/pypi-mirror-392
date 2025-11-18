# WigleSearch.py

`WigleSearch.py` is a command-line tool for querying the [WiGLE API](https://api.wigle.net/) to search for wireless network SSIDs and export the results in either JSON or KML format (for use in Google Earth or other mapping tools).

This script handles pagination, API token-based authentication, and cleanly outputs formatted results suitable for mapping, analysis, or integration with other tools.

Your  API token name and token can be found here: 
https://wigle.net/account

# Install /w PIP
```
pip install wigle-ssid-search
```

---

## 🔧 Features

- Query WiGLE for a specific SSID (e.g. `Starbucks-WiFi`)
- Save results as:
  - `JSON` for analysis or scripting
  - `KML` for visual mapping in tools like Google Earth
- Handles pagination via `searchAfter`
- Respects API rate limits with throttling
- Output file auto-named if not specified

---

## 📦 Requirements

- Python 3.7+
- WiGLE API token and token name (not your WiGLE login username)
- Internet access

# Useage
```
python WigleSearch.py --ssid "YourSSID" --token-name "YourTokenName" --token "YourToken" [--format json|kml] [--output filename] [--max N]

wigle-ssid-search --ssid "YourSSID" --token-name "YourTokenName" --token "YourToken" [--format json|kml] [--output filename] [--max N]
```

## Required arguments:

Argument	Description
--ssid	The SSID name to search for (case sensitive)
--token-name	The WiGLE API token name (not your login email)
--token	Your WiGLE API token

## Optional arguments:

Argument	Description
--format	Output format: json (default) or kml
--output	Output filename (defaults to <SSID>_wigle_results.json/kml)
--max	Maximum number of records to retrieve (default: 1000)
--exact-case Match the SSID with case sensitivity.  


# Example

Search for SSID MyNetwork using your API token.  Export to KML that can be imported into GoogleEarth

```
python WigleSearch.py --ssid "MyNetwork" --token-name "TOKENNAME" --token "YUORTOKEN" --format kml

wigle-ssid-search --ssid "MyNetwork" --token-name "TOKENNAME" --token "YUORTOKEN" --format kml
```

Search for SSID MyNetwork using your API token.  Export to JSON format.

```
python WigleSearch.py --ssid "MyNetwork" --token-name "TOKENNAME" --token "YUORTOKEN" --format json --output wifi_results.json

wigle-ssid-search --ssid "MyNetwork" --token-name "TOKENNAME" --token "YUORTOKEN" --format json --output wifi_results.json
```

# Output Notes

JSON format mirrors the raw WiGLE API result structure (usable for scripting or analysis).

KML output includes placemarks with SSID and BSSID, and GPS coordinates (trilat/trilong) for Google Earth or GIS tools.

# License
MIT License

# Acknowledgments
Built using the public WiGLE API: https://api.wigle.net/api/v2

This tool is unaffiliated with WiGLE.net. Please respect their API Terms of Service.
