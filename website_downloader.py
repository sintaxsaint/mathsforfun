import os
import sys
import urllib.request
import urllib.parse
import urllib.error
import re
from html.parser import HTMLParser

def download_file(url, folder):
    try:
        filename = os.path.basename(urllib.parse.urlparse(url).path)
        if not filename:
            filename = "index.html"
        
        # Remove query parameters from filename
        if '?' in filename:
            filename = filename.split('?')[0]
            
        filepath = os.path.join(folder, filename)
        
        # Avoid overwriting or duplicates if possible, but simple overwrite is fine
        # Check if file exists to save bandwidth? No, always overwrite for freshness
        
        print(f"Downloading {url} to {filepath}...")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            with open(filepath, 'wb') as out_file:
                out_file.write(response.read())
        return filename
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None

class ResourceParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.resources = []

    def handle_starttag(self, tag, attrs):
        for attr, value in attrs:
            if attr in ['src', 'href', 'poster', 'data-src']:
                self.resources.append(value)

def main():
    if len(sys.argv) < 2:
        print("Usage: python website_downloader.py <url>")
        # Default for testing/example
        url = input("Enter URL to download: ").strip()
    else:
        url = sys.argv[1]

    if not url.startswith('http'):
        url = 'https://' + url

    try:
        print(f"Fetching {url}...")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            
        # Create directory for the site
        domain = urllib.parse.urlparse(url).netloc
        folder_name = domain.replace('.', '_').replace(':', '')
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        
        assets_folder = os.path.join(folder_name, 'assets')
        if not os.path.exists(assets_folder):
            os.makedirs(assets_folder)

        # Parse resources
        parser = ResourceParser()
        parser.feed(html_content)
        
        # Download resources and replace links
        # We use simple string replacement which is risky but effective for simple sites
        # A better approach is to reconstruct HTML, but that's complex with standard lib HTMLParser
        
        # Sort resources by length descending to avoid partial replacement issues
        unique_resources = sorted(list(set(parser.resources)), key=len, reverse=True)
        
        for resource_url in unique_resources:
            # Skip empty or anchor links
            if not resource_url or resource_url.startswith('#') or resource_url.startswith('javascript:'):
                continue
                
            # Resolve absolute URL
            absolute_url = urllib.parse.urljoin(url, resource_url)
            
            # Filter out external links if desired? The user wants "entire website".
            # But downloading the entire internet is bad. 
            # We should probably only download assets (images, js, css).
            # If it looks like a page (ends in .html or no extension), maybe skip unless it's the main goal?
            # For now, let's try to download everything that looks like an asset.
            
            ext = os.path.splitext(urllib.parse.urlparse(absolute_url).path)[1].lower()
            is_asset = ext in ['.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot', '.mp3', '.wav', '.mp4', '.webm', '.json', '.xml', '.wasm', '.mem']
            
            if is_asset:
                local_filename = download_file(absolute_url, assets_folder)
                if local_filename:
                    # If it's a CSS file, parse it for more assets
                    if ext == '.css':
                        css_path = os.path.join(assets_folder, local_filename)
                        process_css(css_path, absolute_url, assets_folder)

                    # Replace in HTML
                    # We need to be careful with replacement. 
                    # If resource_url is "style.css", we replace with "assets/style.css"
                    html_content = html_content.replace(resource_url, f'assets/{local_filename}')
            
        # Save HTML
        with open(os.path.join(folder_name, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"Website downloaded to {folder_name}/")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
