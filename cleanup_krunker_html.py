import re
from pathlib import Path

FILE_PATH = Path(r"g:\My Drive\unblocked games\mathsforfun\games\krunker_io\index.html")

def cleanup_html():
    if not FILE_PATH.exists():
        print(f"File not found: {FILE_PATH}")
        return

    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Remove manifest link
    # Pattern: <link rel="manifest" href="assets/manifest.json">
    content = content.replace('<link rel="manifest" href="assets/manifest.json">', '<!-- <link rel="manifest" href="assets/manifest.json"> -->')

    # 2. Remove Google Tag Manager
    # Pattern: <script async src="https://www.googletagmanager.com/gtag/js?id=UA-69264675-5"></script>
    content = content.replace('<script async src="https://www.googletagmanager.com/gtag/js?id=UA-69264675-5"></script>', '<!-- <script async src="https://www.googletagmanager.com/gtag/js?id=UA-69264675-5"></script> -->')

    # 3. Remove/Comment the inline gtag script just in case
    # <script>function gtag(){dataLayer.push(arguments)}window.dataLayer=window.dataLayer||[],gtag("js",new Date),gtag("config","UA-69264675-5")</script>
    gtag_inline = '<script>function gtag(){dataLayer.push(arguments)}window.dataLayer=window.dataLayer||[],gtag("js",new Date),gtag("config","UA-69264675-5")</script>'
    content = content.replace(gtag_inline, f'<!-- {gtag_inline} -->')

    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(content)

    print("Cleanup complete.")

if __name__ == "__main__":
    cleanup_html()
