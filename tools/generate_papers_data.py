#!/usr/bin/env python3
"""
Generate papers-data.js from papers_json folder
Automatically creates the papers list from available JSON files
"""

import json
from pathlib import Path

def generate_papers_data():
    """Generate papers-data.js from papers_json folder"""

    # Get project directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent

    json_dir = project_dir / 'papers_json'
    output_file = project_dir / 'papers-data.js'

    if not json_dir.exists():
        print(f"❌ Error: papers_json directory not found")
        return False

    # Read all JSON files
    papers = []
    json_files = sorted(json_dir.glob('*.json'))

    if not json_files:
        print(f"❌ Error: No JSON files found in papers_json/")
        return False

    print(f"\n{'='*60}")
    print(f"Generating papers-data.js")
    print(f"Found {len(json_files)} paper(s)")
    print(f"{'='*60}\n")

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            paper_id = metadata.get('paper_id', json_file.stem)
            title = metadata.get('title', 'Unknown Title')

            # Check if corresponding HTML exists
            html_file = project_dir / 'papers_html' / f'{paper_id}.html'
            if not html_file.exists():
                print(f"⚠️  Warning: HTML not found for {paper_id}")
                print(f"   Expected: {html_file}")
                continue

            paper = {
                'id': paper_id,
                'name': title,
                'url': f'papers_html/{paper_id}.html'
            }

            papers.append(paper)
            print(f"✓ Added: {paper_id}")
            print(f"  Title: {title[:60]}{'...' if len(title) > 60 else ''}")

        except Exception as e:
            print(f"❌ Error reading {json_file.name}: {e}")
            continue

    if not papers:
        print("\n❌ No valid papers found")
        return False

    # Generate JavaScript file
    js_content = '''/**
 * Available papers for the experiment
 * This file is auto-generated from papers_json/ folder
 * Run: python tools/generate_papers_data.py
 */

const AVAILABLE_PAPERS = [\n'''

    for i, paper in enumerate(papers):
        # Escape single quotes in title
        title = paper['name'].replace("'", "\\'")

        js_content += f'''    {{
        id: '{paper['id']}',
        name: '{title}',
        url: '{paper['url']}'
    }}'''

        if i < len(papers) - 1:
            js_content += ','
        js_content += '\n'

    js_content += '];\n'

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(js_content)

    print(f"\n{'='*60}")
    print(f"✅ Generated: {output_file}")
    print(f"   Total papers: {len(papers)}")
    print(f"{'='*60}\n")

    return True

if __name__ == "__main__":
    success = generate_papers_data()
    exit(0 if success else 1)
