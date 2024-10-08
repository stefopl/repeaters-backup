import csv
import json

def load_csv_data(file_path, delimiter, encoding):
    repeaters = []
    with open(file_path, newline='', encoding=encoding) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delimiter)
        for row in reader:
            repeaters.append(row)
    return repeaters

def save_data(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def convert_csv_to_json(csv_file_details, output_file):
    repeaters = load_csv_data(csv_file_details['file_path'], csv_file_details['delimiter'], csv_file_details['encoding'])
    unique_repeaters = {repeater[csv_file_details['key_field']]: repeater for repeater in repeaters}
    save_data(unique_repeaters, output_file)
    print(f"Data saved to {output_file}")

csv_files = [
    {
        "file_path": 'backup/UKE/club_devices.csv',
        "key_field": 'call_sign',
        "source_name": 'uke_club_devices',
        "delimiter": ';',
        "encoding": 'cp1250'
    },
    {
        "file_path": 'backup/UKE/individual_devices.csv',
        "key_field": 'call_sign',
        "source_name": 'uke_individual_devices',
        "delimiter": ';',
        "encoding": 'cp1250'
    }
]

for csv_file in csv_files:
    output_file_name = f"data/{csv_file['source_name']}.json"
    convert_csv_to_json(csv_file, output_file_name)
