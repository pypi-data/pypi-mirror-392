import json
import argparse
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.dom.minidom
import sys

def create_kml_from_wigle(json_path, output_kml):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{json_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Could not parse JSON - {e}")
        sys.exit(1)

    kml = Element('kml', xmlns='http://www.opengis.net/kml/2.2')
    doc = SubElement(kml, 'Document')
    name = SubElement(doc, 'name')
    name.text = 'WiGLE Networks'

    count = 0
    for result in data.get('results', []):
        ssid = result.get('ssid', 'Unknown SSID')
        lat = result.get('trilat')
        lon = result.get('trilong')
        lastupdt = result.get('lastupdt', 'N/A')
        mac = result.get('netid', 'Unknown MAC')

        if lat is None or lon is None:
            continue  # Skip entries with missing coordinates

        placemark = SubElement(doc, 'Placemark')
        title = SubElement(placemark, 'name')
        title.text = ssid

        desc = SubElement(placemark, 'description')
        desc.text = f"<![CDATA[MAC: {mac}<br/>Last Updated: {lastupdt}]]>"

        point = SubElement(placemark, 'Point')
        coords = SubElement(point, 'coordinates')
        coords.text = f"{lon},{lat},0"

        count += 1

    # Pretty print the KML
    rough_string = tostring(kml, 'utf-8')
    reparsed = xml.dom.minidom.parseString(rough_string)
    pretty_kml = reparsed.toprettyxml(indent="  ")

    with open(output_kml, 'w', encoding='utf-8') as f:
        f.write(pretty_kml)

    print(f"✅ KML file created: {output_kml} ({count} placemarks)")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert WiGLE JSON data to a KML file for Google Earth.')
    parser.add_argument('input_json', help='Path to input WiGLE JSON file')
    parser.add_argument('output_kml', help='Path to output KML file')
    args = parser.parse_args()

    create_kml_from_wigle(args.input_json, args.output_kml)
