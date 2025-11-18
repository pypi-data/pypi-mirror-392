import requests
import json
import time
import argparse
import sys
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.dom.minidom


def fetch_wigle_data(ssid, token_name, api_token, max_results):
    base_url = 'https://api.wigle.net/api/v2/network/search'
    headers = {'accept': 'application/json'}
    params = {
        'onlymine': 'false',
        'freenet': 'false',
        'paynet': 'false',
        'ssid': ssid,
        'resultsPerPage': 100
    }

    all_results = []
    total_fetched = 0
    search_after = None

    print(f"[*] Searching for SSID: {ssid}")

    while total_fetched < max_results:
        if search_after:
            params['searchAfter'] = search_after

        response = requests.get(base_url, headers=headers, params=params, auth=(token_name, api_token))
        if response.status_code != 200:
            print(f"[!] Error {response.status_code}: {response.text}")
            break

        data = response.json()
        results = data.get('results', [])

        if not results:
            print("[*] No more results returned. Ending search.")
            break

        all_results.extend(results)
        total_fetched += len(results)

        print(f"[+] Fetched {len(results)} records (Total: {total_fetched})")

        if 'searchAfter' in data:
            search_after = data['searchAfter']
        else:
            print("[*] No 'searchAfter' field found. Ending search.")
            break

        time.sleep(1)

    return all_results


def filter_case_sensitive(results, target_ssid):
    filtered = [entry for entry in results if entry.get('ssid') == target_ssid]
    print(f"[*] Case-sensitive filtering enabled:")
    print(f"    Total fetched: {len(results)}")
    print(f"    Matched exact SSID '{target_ssid}': {len(filtered)}")
    return filtered


def save_as_json(results, output_file):
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"[✓] Saved {len(results)} records to {output_file} (JSON)")


def save_as_kml(results, output_file):
    kml = Element('kml', xmlns="http://www.opengis.net/kml/2.2")
    doc = SubElement(kml, 'Document')

    for entry in results:
        lat = entry.get('trilat')
        lon = entry.get('trilong')
        ssid = entry.get('ssid', 'unknown')
        bssid = entry.get('netid', 'unknown')

        if lat is None or lon is None:
            continue

        placemark = SubElement(doc, 'Placemark')
        name = SubElement(placemark, 'name')
        name.text = f"{ssid} ({bssid})"

        point = SubElement(placemark, 'Point')
        coords = SubElement(point, 'coordinates')
        coords.text = f"{lon},{lat},0"

    kml_str = xml.dom.minidom.parseString(tostring(kml)).toprettyxml(indent="  ")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(kml_str)

    print(f"[✓] Saved {len(results)} records to {output_file} (KML)")


def main():
    parser = argparse.ArgumentParser(description="Fetch WiGLE results for a given SSID and save as JSON or KML.")
    parser.add_argument('--ssid', required=True, help='SSID to search for')
    parser.add_argument('--token-name', required=True, help='WiGLE Account Token Name (not your login username)')
    parser.add_argument('--token', required=True, help='WiGLE API token (used with the token name)')
    parser.add_argument('--output', default=None, help='Output file (default: <SSID>_wigle_results.json or .kml)')
    parser.add_argument('--max', type=int, default=1000, help='Maximum number of records to fetch (default: 1000)')
    parser.add_argument('--format', choices=['json', 'kml'], default='json', help='Output format: json (default) or kml')
    parser.add_argument('--exact-case', action='store_true', help='Enable case-sensitive filtering on SSID matches')

    args = parser.parse_args()

    output_file = args.output
    if not output_file:
        output_file = f"{args.ssid}_wigle_results.{args.format}"

    results = fetch_wigle_data(args.ssid, args.token_name, args.token, args.max)

    if args.exact_case:
        results = filter_case_sensitive(results, args.ssid)

    if args.format == 'json':
        save_as_json(results, output_file)
    else:
        save_as_kml(results, output_file)


if __name__ == '__main__':
    main()
