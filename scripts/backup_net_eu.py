import os
import requests
import difflib
from datetime import datetime

timestamp_url_1 = 'https://przemienniki.net/export/timestamp.xml'
timestamp_file_path = './backup/przemienniki-net/timestamp.xml'

# Defining filenames along with the export links
export_links_1 = {
    "Native XML Format": {"url": "https://przemienniki.net/export/rxf.xml", "file_name": "rxf.xml"},
    "RT Systems ADMS": {"url": "https://przemienniki.net/export/adms.csv", "file_name": "adms.csv"},
    "Excel": {"url": "https://przemienniki.net/export/przemienniki.xls", "file_name": "przemienniki.xls"},
    "GPX Format": {"url": "https://przemienniki.net/export/przemienniki.gpx", "file_name": "przemienniki.gpx"},
    "KML Format": {"url": "https://przemienniki.net/export/przemienniki.kml", "file_name": "przemienniki.kml"},
    "CHIRP CSV Format": {"url": "https://przemienniki.net/export/chirp.csv?band=2m,70cm&country=pl&onlyworking=true", "file_name": "chirp.csv"},
    "Repeater Radar XML": {"url": "https://przemienniki.net/export/radar.xml", "file_name": "radar.xml"}
}

export_links_2 = {
    "JSON Export": {"url": "https://przemienniki.eu/eksport-danych/json/", "file_name": "przemienniki-eu.json"},
    "CSV Export": {"url": "https://przemienniki.eu/eksport-danych/csv/", "file_name": "przemienniki-eu.csv"},
    "CHIRP CSV Format": {"url": "https://przemienniki.eu/eksport-danych/chirp/?band=70cm,2m&status=working,testing", "file_name": "przemienniki-eu-chirp.csv"}
}

backup_dir_1 = './backup/przemienniki-net/'
backup_dir_2 = './backup/przemienniki-eu/'

session = requests.Session()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
}

def check_timestamp(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    print(f"Failed to check timestamp: {response.status_code} - {response.text}")
    return None

def download_export(link_name, link_info, backup_dir, update_readme=True):
    response = session.get(link_info['url'], headers=headers)
    if response.status_code == 200:
        export_path = os.path.join(backup_dir, link_name.replace(" ", "_"))
        os.makedirs(export_path, exist_ok=True)

        file_name = link_info['file_name']
        with open(os.path.join(export_path, file_name), 'wb') as file:
            file.write(response.content)

        if update_readme:
            with open(os.path.join(export_path, 'README.md'), 'w') as readme:
                readme.write(f"# Backup of: {link_name}\n\n")
                readme.write(f"**Backup Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                readme.write(f"**Link**: [{link_name}]({link_info['url']})\n")
            print(f"README updated for: {link_name}")

        print(f"Downloaded: {link_name} to {export_path}")
    else:
        print(f"Failed to download {link_name}: {response.status_code} - {response.text}")

def compare_files(new_content, existing_file_path):
    with open(existing_file_path, 'rb') as existing_file:
        existing_content = existing_file.read()

    new_content_str = new_content.decode('utf-8')
    existing_content_str = existing_content.decode('utf-8')

    diff = difflib.unified_diff(
        existing_content_str.splitlines(),
        new_content_str.splitlines(),
        fromfile='existing_file',
        tofile='new_file',
        lineterm=''
    )

    for line in diff:
        print(line)

def main():
    print("Checking timestamp...")
    current_timestamp = check_timestamp(timestamp_url_1)
    
    if current_timestamp:
        print("Timestamp fetched successfully.")
        if os.path.exists(timestamp_file_path):
            with open(timestamp_file_path, 'r') as file:
                saved_timestamp = file.read()
            if saved_timestamp == current_timestamp:
                print("Timestamp has not changed. No further downloads needed for .net exports.")
            else:
                print("Timestamp has changed. Downloading .net exports...")
                os.makedirs(os.path.dirname(timestamp_file_path), exist_ok=True)
                with open(timestamp_file_path, 'w') as file:
                    file.write(current_timestamp)
                for name, info in export_links_1.items():
                    download_export(name, info, backup_dir_1)
        else:
            print("No previous timestamp found. Downloading .net exports...")
            os.makedirs(os.path.dirname(timestamp_file_path), exist_ok=True)
            with open(timestamp_file_path, 'w') as file:
                file.write(current_timestamp)
            for name, info in export_links_1.items():
                download_export(name, info, backup_dir_1)

    print("Downloading .eu exports...")
    for name, info in export_links_2.items():
        export_path = os.path.join(backup_dir_2, name.replace(" ", "_"))
        file_name = info['file_name']
        existing_file_path = os.path.join(export_path, file_name)

        if os.path.exists(existing_file_path):
            # Download only if the content has changed
            new_response = session.get(info['url'], headers=headers)
            if new_response.status_code == 200:
                if new_response.content != b'':  # Make sure there's content
                    print(f"Export file already exists for {name}. Checking for updates...")
                    if new_response.content != open(existing_file_path, 'rb').read():
                        print(f"Changes detected for {name}. Downloading updated export...")
                        download_export(name, info, backup_dir_2)
                    else:
                        print(f"No changes detected for {name}. README will not be modified.")
                else:
                    print(f"Empty response for {name}. No download performed.")
        else:
            download_export(name, info, backup_dir_2)

if __name__ == "__main__":
    main()
