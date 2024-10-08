import requests
import csv
import zipfile
import os
from io import StringIO
from datetime import datetime

csv_url = "https://api.dane.gov.pl/1.4/datasets/1051/resources/metadata.csv?lang=pl"
backup_dir = "./backup/UKE"

os.makedirs(backup_dir, exist_ok=True)

response = requests.get(csv_url)
response.raise_for_status()

csv_data = StringIO(response.content.decode('utf-8'))
csv_reader = csv.DictReader(csv_data, delimiter=';')

latest_url = None
latest_date = None

for row in csv_reader:

    try:
        file_date = datetime.fromisoformat(row['Data udostępnienia danych'].replace('Z', '+00:00'))
    except (ValueError, KeyError):
        continue

    if latest_date is None or file_date > latest_date:
        latest_date = file_date
        latest_url = row['URL pliku (do pobrania)']

if latest_url:
    zip_response = requests.get(latest_url)
    zip_path = os.path.join(backup_dir, "latest_file.zip")

    with open(zip_path, 'wb') as zip_file:
        zip_file.write(zip_response.content)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(backup_dir)

    print(f"Latest file downloaded and extracted to {backup_dir}")

    for filename in zip_ref.namelist():
        name, ext = os.path.splitext(filename)

        new_name = "_".join(part for part in name.split("_") if not part[0].isdigit())

        old_file_path = os.path.join(backup_dir, filename)
        new_file_path = os.path.join(backup_dir, new_name + ext)  # Append the extension

        os.rename(old_file_path, new_file_path)

else:
    print("No file found.")
