import csv
import json
from datetime import datetime

def generate_unique_key(existing_data, base_key):
    unique_key = base_key
    counter = 2

    while unique_key in existing_data:
        unique_key = f"{base_key}_{counter}"
        counter += 1

    return unique_key

def process_new_repeaters(new_repeaters, key_field):
    unique_repeaters = []
    existing_callsigns = {}

    for repeater in new_repeaters:
        base_callsign = repeater[key_field]

        if base_callsign in existing_callsigns:
            unique_callsign = generate_unique_key(existing_callsigns, base_callsign)
            repeater[key_field] = unique_callsign
        else:
            unique_callsign = base_callsign

        existing_callsigns[unique_callsign] = True
        unique_repeaters.append(repeater)

    return unique_repeaters

def load_existing_data(output_file):
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_csv_data(file_path, delimiter, encoding):
    repeaters = []
    with open(file_path, newline='', encoding=encoding) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delimiter)
        for row in reader:
            repeaters.append(row)
    return repeaters

def update_repeater_data(existing_data, new_repeaters, key_field):
    updated_data = existing_data.copy()
    current_edit_date = datetime.now().strftime("%Y-%m-%d")

    for new_repeater in new_repeaters:
        key = new_repeater[key_field]

        if key in existing_data:
            existing_repeater = existing_data[key]
            new_repeater["edit_date"] = "2023-01-01"
            if existing_repeater != new_repeater:
                new_repeater["edit_date"] = current_edit_date
                updated_data[key] = new_repeater
            else:
                updated_data[key] = existing_repeater
        else:
            new_repeater["edit_date"] = "2023-01-01"
            updated_data[key] = new_repeater

    return updated_data


def update_repeater_data_from_csv(csv_file_details, output_file):

    existing_data = load_existing_data(output_file)
    new_repeaters = load_csv_data(csv_file_details['file_path'], csv_file_details['delimiter'], csv_file_details['encoding'])
    unique_repeaters = process_new_repeaters(new_repeaters, csv_file_details['key_field'])
    updated_data = update_repeater_data(existing_data, unique_repeaters, csv_file_details['key_field'])
    save_data(updated_data, output_file)
    print(f"Data saved to {output_file}")

csv_file_details = {
    "file_path": 'backup/przemienniki-eu/CSV_Export/przemienniki-eu.csv',
    "key_field": 'Callsign',
    "source_name": 'przemienniki_eu',
    "delimiter": ',',
    "encoding": 'utf-8'
}
output_file = 'data/przemienniki_eu.json'

update_repeater_data_from_csv(csv_file_details, output_file)
