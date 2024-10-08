import json
import xml.etree.ElementTree as ET
import csv

def load_xml_data_from_file(file_path, key_field, source_name):
    data = {}
    tree = ET.parse(file_path)
    root = tree.getroot()

    print(f"Loading XML data from {file_path}...")
    for repeater in root.findall('.//repeater'):
        key = repeater.find(key_field).text
        if key:
            if key not in data:
                data[key] = {}
            source_data = {}

            def process_element(element, parent_key=""):
                for child in element:
                    child_key = f"{parent_key}{child.tag}"
                    if child.attrib:
                        child_key += f"_{child.attrib.get('type', 'default')}"
                    if len(child) > 0:
                        process_element(child, f"{child_key}_")
                    else:
                        source_data[child_key] = child.text

            process_element(repeater)
            data[key][source_name] = source_data

    print(f"Loaded {len(data)} entries from {file_path}.")
    return data

def load_csv_data_from_file(file_path, key_field, source_name, delimiter=',', encoding='utf-8'):
    data = {}
    with open(file_path, mode='r', encoding=encoding) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delimiter)
        print(f"Loading CSV data from {file_path}...")
        for row in reader:
            key = row[key_field]
            if key:
                if key not in data:
                    data[key] = {}
                data[key][source_name] = row

    print(f"Loaded {len(data)} entries from {file_path}.")
    return data

def save_to_json(data, output_file):

    os.makedirs('data', exist_ok=True)

    output_path = os.path.join('data', output_file)

    with open(output_file, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, ensure_ascii=False, indent=4)
    print(f"Data has been saved to {output_file}.")

file_paths = [
    {
        "file_path": 'backup/przemienniki-net/Native_XML_Format/rxf.xml',
        "key_field": 'qra',
        "source_name": 'przemienniki_net',
        "delimiter": None,
        "encoding": 'utf-8'
    },
    {
        "file_path": 'backup/przemienniki-eu/CSV_Export/przemienniki-eu.csv',
        "key_field": 'Callsign',
        "source_name": 'przemienniki_eu',
        "delimiter": ',',
        "encoding": 'utf-8'
    },
    {
        "file_path": 'backup/UKE/club_devices.csv',
        "key_field": 'call_sign',
        "source_name": 'UKE_club_devices',
        "delimiter": ';',
        "encoding": 'ISO-8859-1'
    },
    {
        "file_path": 'backup/UKE/individual_devices.csv',
        "key_field": 'call_sign',
        "source_name": 'UKE_individual_devices',
        "delimiter": ';',
        "encoding": 'ISO-8859-1'
    }
]

if __name__ == "__main__":
    merged_data = {}

    for entry in file_paths:
        added_count = 0
        updated_count = 0

        if entry["file_path"].endswith('.xml'):
            xml_data = load_xml_data_from_file(entry["file_path"], entry["key_field"], entry["source_name"])
            for key, value in xml_data.items():
                if key not in merged_data:
                    merged_data[key] = value
                    added_count += 1
                else:
                    merged_data[key].update(value)
                    updated_count += 1

        elif entry["file_path"].endswith('.csv'):
            csv_data = load_csv_data_from_file(
                entry["file_path"],
                entry["key_field"],
                entry["source_name"],
                entry["delimiter"],
                entry["encoding"]
            )
            for key, value in csv_data.items():
                if key not in merged_data:
                    merged_data[key] = value
                    added_count += 1
                else:
                    merged_data[key].update(value)
                    updated_count += 1

        print(f"For {entry['source_name']}: Added {added_count}, Updated {updated_count}")

    save_to_json(merged_data, 'merged_data.json')
