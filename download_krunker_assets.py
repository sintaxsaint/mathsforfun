import os
import re
import urllib.request
import urllib.parse
from pathlib import Path

# Configuration
BASE_DIR = Path(r"g:\My Drive\unblocked games\mathsforfun\games\krunker_io")
ASSETS_DIR = BASE_DIR / "assets"
LOCAL_ASSETS_DIR = ASSETS_DIR / "local"

# Files to process
FILES_TO_PROCESS = [
    ASSETS_DIR / "flag.css",
    ASSETS_DIR / "main.css",
    BASE_DIR / "index.html"
]

# URL Pattern
URL_PATTERN = re.compile(r'https://assets\.krunker\.io/([^"\'\)\s]*)')

def download_file(url, local_path):
    try:
        local_path.parent.mkdir(parents=True, exist_ok=True)
        if not local_path.exists():
            print(f"Downloading: {url} -> {local_path}")
            # Add headers to mimic a browser to avoid potential 403s
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req) as response, open(local_path, 'wb') as out_file:
                out_file.write(response.read())
        else:
            print(f"Skipping (exists): {local_path}")
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False

def process_file(file_path):
    print(f"Processing {file_path}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Fallback for binary/mixed files if needed, though these should be text
        with open(file_path, 'r', encoding='latin-1') as f:
            content = f.read()

    # Find all matches
    matches = list(set(URL_PATTERN.findall(content))) # unique matches
    
    if not matches:
        print(f"No assets.krunker.io references found in {file_path.name}")
        return

    print(f"Found {len(matches)} unique assets in {file_path.name}")

    replacements = {}

    for relative_url_part in matches:
        # Clean up URL part (remove query params for filename)
        full_url = f"https://assets.krunker.io/{relative_url_part}"
        
        # Handle query parameters for local storage
        parsed_url = urllib.parse.urlparse(full_url)
        path_only = parsed_url.path.lstrip('/') # e.g. img/flags/3x2/AF.svg
        
        # Construct local path
        local_file_path = LOCAL_ASSETS_DIR / path_only
        
        # Download
        download_file(full_url, local_file_path)
        
        # Calculate relative path for replacement
        # If we are in assets/flag.css, local assets are in assets/local/...
        # So relative path is local/...
        # If we are in index.html, assets are in assets/local/...
        
        if file_path.parent == ASSETS_DIR:
            # e.g. from assets/flag.css to assets/local/img/... -> local/img/...
            replacement_path = f"local/{path_only}"
        elif file_path.parent == BASE_DIR:
            # e.g. from index.html to assets/local/img/... -> assets/local/img/...
            replacement_path = f"assets/local/{path_only}"
        else:
            # Fallback
            replacement_path = f"assets/local/{path_only}"

        # Store replacement (original match string from regex might include query params)
        # We need to replace the exact string found in the file
        # The regex captured everything after domain.
        
        # Reconstruct the full match string as it appears in file
        original_string = f"https://assets.krunker.io/{relative_url_part}"
        replacements[original_string] = replacement_path

    # Apply replacements
    new_content = content
    for old, new in replacements.items():
        new_content = new_content.replace(old, new)
        
    # Special cleanup: Comment out dns-prefetch if present
    if file_path.name == "index.html":
        new_content = new_content.replace('<link rel="dns-prefetch" href="//assets.krunker.io">', '<!-- <link rel="dns-prefetch" href="//assets.krunker.io"> -->')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Updated {file_path.name}")

def main():
    if not BASE_DIR.exists():
        print(f"Error: Base directory not found: {BASE_DIR}")
        return

    for file_path in FILES_TO_PROCESS:
        if file_path.exists():
            process_file(file_path)
        else:
            print(f"Warning: File not found: {file_path}")

if __name__ == "__main__":
    main()
