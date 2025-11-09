#!/usr/bin/env python3
"""
Paper Integration Tool
Integrates reviewed HTML papers into the experiment system
"""

import json
import sys
from pathlib import Path

def load_paper_metadata(paper_id, project_dir):
    """Load paper metadata from JSON"""
    json_path = project_dir / 'papers_json' / f'{paper_id}.json'
    
    if not json_path.exists():
        print(f"❌ Error: Metadata not found for '{paper_id}'")
        print(f"   Expected: {json_path}")
        return None
    
    with open(json_path, 'r') as f:
        return json.load(f)

def load_paper_html(paper_id, project_dir):
    """Load paper HTML content"""
    html_path = project_dir / 'papers_html' / f'{paper_id}.html'
    
    if not html_path.exists():
        print(f"❌ Error: HTML not found for '{paper_id}'")
        print(f"   Expected: {html_path}")
        return None
    
    with open(html_path, 'r') as f:
        return f.read()

def extract_paper_content(html):
    """Extract just the paper content div from full HTML"""
    import re
    
    # Find the main content div
    match = re.search(r'(<div class="prose max-w-none">.*?</div>\s*</div>)', html, re.DOTALL)
    if match:
        return match.group(1)
    
    return None

def generate_papers_list(paper_ids, project_dir):
    """Generate JavaScript papers array"""
    papers = []
    
    for paper_id in paper_ids:
        metadata = load_paper_metadata(paper_id, project_dir)
        if metadata:
            papers.append({
                'id': paper_id,
                'name': metadata['title'],
                'file': f'{paper_id}.pdf',
                'sections': [s['title'] for s in metadata['sections']]
            })
    
    return papers

def create_experiment_html(paper_ids, project_dir):
    """Create experiment HTML with integrated papers"""
    
    print(f"\n{'='*60}")
    print("Integrating Papers into Experiment System")
    print(f"{'='*60}\n")
    
    # Load all paper data
    papers_data = {}
    for paper_id in paper_ids:
        print(f"Loading: {paper_id}")
        metadata = load_paper_metadata(paper_id, project_dir)
        html = load_paper_html(paper_id, project_dir)
        
        if not metadata or not html:
            print(f"  ❌ Skipping {paper_id} due to missing files")
            continue
        
        content = extract_paper_content(html)
        if not content:
            print(f"  ❌ Failed to extract content from {paper_id}")
            continue
        
        papers_data[paper_id] = {
            'metadata': metadata,
            'content': content
        }
        print(f"  ✓ Loaded successfully")
    
    if not papers_data:
        print("\n❌ No papers loaded. Aborting.")
        return None
    
    # Generate papers list for dropdown
    papers_list = generate_papers_list(list(papers_data.keys()), project_dir)
    
    # Read experiment template
    template_path = project_dir / 'experiment_template.html'
    if not template_path.exists():
        print(f"\n❌ Template not found: {template_path}")
        print("   Creating from base experiment file...")
        # Here we would copy from the base experiment file
        return None
    
    with open(template_path, 'r') as f:
        experiment_html = f.read()
    
    # Generate paper contents as JavaScript object
    papers_content_js = "const papersContent = {\n"
    for paper_id, data in papers_data.items():
        # Escape content for JavaScript
        content_escaped = data['content'].replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
        papers_content_js += f"  '{paper_id}': `{content_escaped}`,\n"
    papers_content_js += "};\n"
    
    # Generate section boundaries as JavaScript object
    papers_sections_js = "const papersSections = {\n"
    for paper_id, data in papers_data.items():
        sections = {}
        for i, section in enumerate(data['metadata']['sections']):
            sections[section['title']] = {
                'start': i * 600,
                'end': (i + 1) * 600
            }
        papers_sections_js += f"  '{paper_id}': {json.dumps(sections, indent=4)},\n"
    papers_sections_js += "};\n"
    
    # TODO: Insert into experiment template
    # This would require the actual template structure
    
    print(f"\n{'='*60}")
    print(f"✓ Processed {len(papers_data)} papers")
    print("Papers:")
    for p in papers_list:
        print(f"  - {p['id']}: {p['name']}")
        print(f"    Sections: {', '.join(p['sections'])}")
    print(f"{'='*60}\n")
    
    return papers_list

def list_available_papers(project_dir):
    """List all available papers"""
    json_dir = project_dir / 'papers_json'
    
    if not json_dir.exists():
        print("No papers found.")
        return []
    
    papers = []
    for json_file in sorted(json_dir.glob('*.json')):
        with open(json_file, 'r') as f:
            metadata = json.load(f)
            papers.append({
                'id': metadata['paper_id'],
                'title': metadata['title'],
                'sections': len(metadata['sections'])
            })
    
    return papers

def main():
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    
    # If no arguments, list available papers
    if len(sys.argv) < 2:
        print("\nAvailable Papers:")
        print("="*60)
        papers = list_available_papers(project_dir)
        if not papers:
            print("  No papers found. Convert PDFs first using convert_paper.py")
        else:
            for i, paper in enumerate(papers, 1):
                print(f"{i}. {paper['id']}")
                print(f"   Title: {paper['title']}")
                print(f"   Sections: {paper['sections']}")
                print()
        
        print("Usage:")
        print("  python integrate_papers.py <paper_id1> [paper_id2] ...")
        print("\nExample:")
        print("  python integrate_papers.py chi2025-students-reading-ai")
        print("  python integrate_papers.py paper1 paper2 paper3")
        return
    
    # Get paper IDs from arguments
    paper_ids = sys.argv[1:]
    
    # Integrate papers
    create_experiment_html(paper_ids, project_dir)
    
    print("👉 Next Steps:")
    print("   1. Open experiment.html in browser")
    print("   2. Test with each paper")
    print("   3. Run experiment with participants")

if __name__ == "__main__":
    main()
