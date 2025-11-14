#!/usr/bin/env python3
"""
Extract clean content from ACM HTML without BeautifulSoup
Uses simple regex and string manipulation
"""

import sys
import json
import re
from pathlib import Path

def extract_clean_content(html_path, json_path, output_path):
    """Extract main content from ACM HTML"""

    # Read original HTML
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Read metadata
    with open(json_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    title = metadata.get('title', 'Paper')
    paper_id = metadata.get('paper_id', 'unknown')

    # Find abstract section
    abstract_match = re.search(r'<section id="summary-abstract"[^>]*>(.*?)</section>', html, re.DOTALL)
    abstract_html = abstract_match.group(1) if abstract_match else ''

    # Find body matter section
    body_match = re.search(r'<section id="bodymatter"[^>]*>(.*?)</section>\s*</div>\s*</div>\s*<div', html, re.DOTALL)
    body_html = body_match.group(1) if body_match else ''

    if not body_html:
        print("Warning: Could not find bodymatter section")
        body_html = "<p>Content extraction failed</p>"

    # Combine abstract and body
    content_html = abstract_html + body_html

    # Fix image paths - convert ACM paths to local paths
    content_html = re.sub(
        r'src="[^"]*/(chiea25-\d+-fig\d+\.jpg)"',
        rf'src="../papers_images/{paper_id}/\1"',
        content_html
    )

    # Generate final HTML
    final_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* ACM content styling */
        .prose a {{ color: #2563eb; text-decoration: underline; }}
        .prose figure {{ margin: 2rem 0; }}
        .prose figcaption {{ margin-top: 0.5rem; font-size: 0.875rem; color: #6b7280; }}
        .prose table {{ border-collapse: collapse; width: 100%; margin: 2rem 0; }}
        .prose th, .prose td {{ border: 1px solid #d1d5db; padding: 0.5rem; }}
        .prose th {{ background-color: #f3f4f6; font-weight: bold; }}
    </style>
</head>
<body class="bg-gray-50 p-8">
    <!-- Paper ID: {paper_id} -->

    <div class="max-w-4xl mx-auto bg-white shadow-xl rounded-lg p-12">
        <div class="prose max-w-none" id="paper-content">
            <h1 class="text-4xl font-bold mb-4">{title}</h1>
{content_html}
        </div>
    </div>
</body>
</html>
'''

    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_html)

    print(f"✓ Extracted content saved: {output_path}")
    return True

def main():
    if len(sys.argv) < 4:
        print("""
Extract Clean Content from ACM HTML
====================================

Usage:
  python extract_acm_content.py <html_file> <json_file> <output_file>

Example:
  python extract_acm_content.py \\
    ../papers_html/chi2025-older-adults-personality.html \\
    ../papers_json/chi2025-older-adults-personality.json \\
    ../papers_html/chi2025-older-adults-personality.html
""")
        sys.exit(1)

    html_path = Path(sys.argv[1])
    json_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3])

    if not html_path.exists():
        print(f"Error: HTML file not found: {html_path}")
        sys.exit(1)

    if not json_path.exists():
        print(f"Error: JSON file not found: {json_path}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"Extracting clean content from ACM HTML")
    print(f"Input: {html_path.name}")
    print(f"Output: {output_path.name}")
    print(f"{'='*60}\n")

    success = extract_clean_content(html_path, json_path, output_path)

    if success:
        print(f"\n{'='*60}")
        print("✅ Done! Paper is ready for experiment.")
        print(f"{'='*60}\n")
    else:
        print("❌ Failed to extract content")
        sys.exit(1)

if __name__ == "__main__":
    main()
