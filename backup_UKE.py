import requests
import csv
import zipfile
import os
from io import StringIO
from datetime import datetime

# Define the URL to download the CSV metadata
csv_url = "https://api.dane.gov.pl/1.4/datasets/1051/resources/metadata.csv?lang=pl"

# Directory to store the extracted files
backup_dir = "./backup-repo/UKE"

# Create the backup directory if it doesn't exist
os.makedirs(backup_dir, exist_ok=True)

# Fetch the CSV data
response = requests.get(csv_url)
response.raise_for_status()

# Parse the CSV data with explicit UTF-8 encoding
csv_data = StringIO(response.content.decode('utf-8'))
csv_reader = csv.DictReader(csv_data, delimiter=';')

# Initialize variables to store the latest file information
latest_url = None
latest_date = None

# Iterate through each row in the CSV and find the file with the highest date
for row in csv_reader:

    # Parse the 'Data udostępnienia danych' field to datetime
    try:
        file_date = datetime.fromisoformat(row['Data udostępnienia danych'].replace('Z', '+00:00'))
    except (ValueError, KeyError):
        continue
    
    # Find the latest file
    if latest_date is None or file_date > latest_date:
        latest_date = file_date
        latest_url = row['URL pliku (do pobrania)']

# Download and extract the latest file if available
if latest_url:
    # Download the zip file
    zip_response = requests.get(latest_url)
    zip_path = os.path.join(backup_dir, "latest_file.zip")

    # Save the zip file
    with open(zip_path, 'wb') as zip_file:
        zip_file.write(zip_response.content)

    # Extract the zip file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(backup_dir)

    print(f"Latest file downloaded and extracted to {backup_dir}")

    # Rename the extracted files to remove the date
    for filename in zip_ref.namelist():
        # Split the filename into name and extension
        name, ext = os.path.splitext(filename)  # Get the name and extension

        # Remove the date part from the filename
        new_name = "_".join(part for part in name.split("_") if not part[0].isdigit())
        
        # Construct full file paths
        old_file_path = os.path.join(backup_dir, filename)
        new_file_path = os.path.join(backup_dir, new_name + ext)  # Append the extension

        # Rename the file
        os.rename(old_file_path, new_file_path)

else:
    print("No file found.")
