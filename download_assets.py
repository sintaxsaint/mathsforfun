import os
import re
import urllib.request
import urllib.error
from urllib.parse import urljoin, urlparse

targets = [
    {
        "dir": "games/bloxorz",
        "base": "https://www.coolmathgames.com/sites/default/files/public_games/48807/"
    },
    {
        "dir": "games/sugar-sugar",
        "base": "https://www.coolmathgames.com/sites/default/files/public_games/49756/"
    },
    {
        "dir": "games/worlds-hardest-game",
        "base": "https://www.coolmathgames.com/sites/default/files/public_games/48362/"
    }
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

for target in targets:
    local_dir = os.path.abspath(target["dir"])
    base_url = target["base"]
    index_path = os.path.join(local_dir, "index.html")
    
    print(f"Processing {local_dir}...")
    
    if not os.path.exists(index_path):
        print(f"  Error: {index_path} not found.")
        continue
        
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    patterns = [
        r'src=["\']([^"\']+)["\']',
        r'href=["\']([^"\']+)["\']'
    ]
    
    resources = set()
    for p in patterns:
        matches = re.findall(p, content)
        for m in matches:
            if m.startswith('http') or m.startswith('//') or m.startswith('#') or m.startswith('mailto:') or m.startswith('javascript:') or m.startswith('data:'):
                continue
            # Skip the back button we added
            if 'index.html' in m and '..' in m:
                continue
            resources.add(m)
            
    print(f"  Found {len(resources)} potential resources from HTML.")
    
    # Phase 2: Download HTML resources
    downloaded_files = []
    for res in resources:
        parsed = urlparse(res)
        clean_path = parsed.path
        
        if not clean_path or clean_path.endswith('/'):
            continue

        remote_url = urljoin(base_url, res)
        local_res_path = os.path.join(local_dir, clean_path.lstrip('/'))
        
        if not os.path.abspath(local_res_path).startswith(local_dir):
            continue

        os.makedirs(os.path.dirname(local_res_path), exist_ok=True)
        
        if not os.path.exists(local_res_path):
            print(f"    Downloading {clean_path} from {remote_url}...")
            try:
                req = urllib.request.Request(remote_url, headers=headers)
                with urllib.request.urlopen(req) as response:
                    data = response.read()
                    with open(local_res_path, 'wb') as f_out:
                        f_out.write(data)
                    downloaded_files.append(local_res_path)
            except Exception as e:
                print(f"    Failed to download {clean_path}: {e}")
        else:
            downloaded_files.append(local_res_path)

    # Phase 3: Scan downloaded files for secondary assets
    print("  Scanning downloaded files for secondary assets...")
    secondary_assets = set()
    asset_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.mp3', '.wav', '.ogg', '.json', '.xml', '.fnt')
    
    # Also scan the index.html again for hidden assets
    files_to_scan = downloaded_files + [index_path]
    
    for file_path in files_to_scan:
        if not os.path.exists(file_path): continue
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Find strings that look like filenames
                # "something.png", 'something.png', url(something.png)
                # We'll look for anything ending in extensions
                for ext in asset_extensions:
                    # Regex: ["'(]([^"'\)\n]+?\.png)["'\)]
                    pattern = r'["\'\(]([^"\'\)\n]+?' + re.escape(ext) + r')["\'\)]'
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for m in matches:
                        if 'http' in m or '//' in m: continue
                        secondary_assets.add(m)
        except Exception as e:
            print(f"    Error scanning {file_path}: {e}")

    print(f"  Found {len(secondary_assets)} potential secondary assets.")
    for res in secondary_assets:
        parsed = urlparse(res)
        clean_path = parsed.path
        if not clean_path or clean_path.endswith('/'): continue
        
        remote_url = urljoin(base_url, res)
        local_res_path = os.path.join(local_dir, clean_path.lstrip('/'))
        
        if not os.path.abspath(local_res_path).startswith(local_dir): continue
        
        os.makedirs(os.path.dirname(local_res_path), exist_ok=True)
        
        if not os.path.exists(local_res_path):
            print(f"    Downloading secondary {clean_path}...")
            try:
                req = urllib.request.Request(remote_url, headers=headers)
                with urllib.request.urlopen(req) as response:
                    data = response.read()
                    with open(local_res_path, 'wb') as f_out:
                        f_out.write(data)
            except Exception as e:
                # Many might be false positives, so don't spam errors too much
                pass
