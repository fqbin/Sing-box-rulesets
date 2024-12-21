#!/bin/python3
import requests
import json
import subprocess
import os
import shutil

# Recursive function to extract domains
def extract_domains(data):
    domains = []
    for key, value in data.items():
        if isinstance(value, dict):
            domains.extend(extract_domains(value))
        elif isinstance(value, list):
            domains.extend(value)
    return domains

# Fetch the raw JSON from the URL
url = "https://raw.githubusercontent.com/1-stream/1stream-public-utils/refs/heads/main/stream.list.json"
response = requests.get(url)

# Check if the request was successful
if response.status_code != 200:
    print("Failed to fetch the JSON file")
    exit(1)

# Parse the JSON response
data = response.json()

# Extract domains using the recursive function
domains = extract_domains(data)

# Remove duplicates by converting to a set and back to a list
domains = list(set(domains))

# Create the target JSON structure
target_json = {
    "version": 2,
    "rules": [
        {
            "domain_suffix": domains
        }
    ]
}

# Path to the output JSON file
output_file_path = 'stream.json'

# Write the result to the output JSON file
with open(output_file_path, 'w') as output_file:
    json.dump(target_json, output_file, indent=2)

print(f"Domain extraction and JSON creation complete. Check '{output_file_path}'.")

# Compile the sing-box rule-set using the target JSON
try:
    # Run the 'sing-box rule-set compile' command
    result = subprocess.run(['sing-box', 'rule-set', 'compile', output_file_path], capture_output=True, text=True)

    # Check if the command was successful
    if result.returncode == 0:
        print("sing-box rule-set compile was successful.")
        print(result.stdout)

        # Check if the stream.srs file exists
        output_srs_path = 'stream.srs'
        if os.path.exists(output_srs_path):
            print(f"Moving {output_srs_path} to /var/www/html/public/stream/")

            # Ensure the target directory exists
            target_dir = '/var/www/html/public/stream/'
            os.makedirs(target_dir, exist_ok=True)

            # Move the stream.srs file to the target directory
            shutil.move(output_srs_path, os.path.join(target_dir, 'stream.srs'))
            print(f"File moved to {target_dir} successfully.")
        else:
            print("Error: 'stream.srs' file was not generated.")
    else:
        print("Error during sing-box rule-set compile:")
        print(result.stderr)
except FileNotFoundError:
    print("Error: 'sing-box' command not found. Make sure sing-box is installed and in the system PATH.")
except Exception as e:
    print(f"An error occurred: {e}")