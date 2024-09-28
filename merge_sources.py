import xml.etree.ElementTree as ET
import csv
import os  # Import os to check for file existence

# Function to load XML data from a local file
def load_xml_data_from_file(file_path, key_field, source_name):
    data = {}
    try:
        tree = ET.parse(file_path)  # Load the XML file
        root = tree.getroot()
        
        print(f"Loading XML data from {file_path}...")
        for repeater in root.findall('.//repeater'):
            key = repeater.find(key_field).text
            if key:
                if key not in data:
                    data[key] = {}  # Initialize as an empty dictionary
                
                # Initialize a dictionary to hold all repeater data
                source_data = {}
                
                # Helper function to recursively process elements
                def process_element(element, parent_key=""):
                    for child in element:
                        # Create a new key using the tag and the parent key
                        child_key = f"{parent_key}{child.tag}"
                        if child.attrib:
                            # Check if the element has attributes
                            child_key += f"_{child.attrib.get('type', 'default')}"  # Append the type if available
                        # Check if the child has sub-elements
                        if len(child) > 0:
                            # Recursive call to process sub-elements
                            process_element(child, f"{child_key}_")
                        else:
                            # Add text to source_data
                            source_data[child_key] = child.text
                
                # Call the helper function for the main repeater element
                process_element(repeater)
                
                # Assign the flattened data to the repeater under the specified source name
                data[key][source_name] = source_data
        
        print(f"Loaded {len(data)} entries from {file_path}.")
    except FileNotFoundError:
        print(f"File not found: {file_path}. Skipping.")
    return data

# Function to load CSV data from a local file
def load_csv_data_from_file(file_path, key_field, source_name):
    data = {}
    try:
        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            print(f"Loading CSV data from {file_path}...")
            for row in reader:
                key = row[key_field]
                if key:
                    if key not in data:
                        data[key] = {}  # Initialize as an empty dictionary
                    data[key][source_name] = row  # Add the row data under the source name
            
        print(f"Loaded {len(data)} entries from {file_path}.")
    except FileNotFoundError:
        print(f"File not found: {file_path}. Skipping.")
    return data

# Define the file paths, call sign fields, and source names
file_paths = [
    {
        "file_path": 'backup-repo/przemienniki-net/Native_XML_Format/rxf.xml',
        "key_field": 'qra',  # Key field for XML
        "source_name": 'przemienniki_net'
    },
    {
        "file_path": 'backup-repo/przemienniki-eu/CSV_Export/przemienniki-eu.csv',
        "key_field": 'Callsign',  # Key field for CSV
        "source_name": 'przemienniki.eu'
    },
    {
        "file_path": 'backup-repo/UKE/individual_devices.csv',
        "key_field": 'call_sign',  # Key field for CSV
        "source_name": 'UKE_individual_devices'
    },
    {
        "file_path": 'backup-repo/UKE/club_devices.csv',
        "key_field": 'call_sign',  # Key field for CSV
        "source_name": 'UKE_club_devices'
    }
]

# Example usage
if __name__ == "__main__":
    # Load XML and CSV data
    for entry in file_paths:
        if os.path.exists(entry["file_path"]):  # Check if the file exists
            if entry["file_path"].endswith('.xml'):
                xml_data = load_xml_data_from_file(entry["file_path"], entry["key_field"], entry["source_name"])
            elif entry["file_path"].endswith('.csv'):
                csv_data = load_csv_data_from_file(entry["file_path"], entry["key_field"], entry["source_name"])
        else:
            print(f"File does not exist: {entry['file_path']}. Skipping.")
