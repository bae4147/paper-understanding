#!/usr/bin/env python3
"""
PDF to HTML Converter for Reading Experiment
Converts academic papers (PDF) to single-column HTML format
"""

import fitz  # PyMuPDF
import re
import json
import sys
from pathlib import Path

class PaperConverter:
    def __init__(self):
        # Common academic paper section headers
        self.section_keywords = [
            'ABSTRACT', 
            'INTRODUCTION', 
            'BACKGROUND', 
            'RELATED WORK', 
            'LITERATURE REVIEW',
            'METHODOLOGY', 
            'METHOD', 
            'METHODS', 
            'APPROACH',
            'RESEARCH CONTEXT',
            'RESEARCH CONTEXT AND APPROACH',
            'RESULTS', 
            'FINDINGS', 
            'DISCUSSION', 
            'CONCLUSION',
            'CONCLUSIONS',
            'FUTURE WORK', 
            'LIMITATIONS', 
            'REFERENCES', 
            'ACKNOWLEDGMENTS',
            'ACKNOWLEDGEMENTS'
        ]
    
    def extract_pdf_content(self, pdf_path):
        """Extract text and structure from PDF"""
        doc = fitz.open(pdf_path)
        
        full_text = ""
        
        # Extract all text
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            full_text += text + "\n"
        
        doc.close()
        
        # Parse structure
        return self._parse_structure(full_text)
    
    def _parse_structure(self, text):
        """Parse text to identify sections and content"""
        lines = text.split('\n')
        content = []
        sections = []
        current_section = None
        section_start_pos = 0
        
        # First, extract title and authors (usually first few lines)
        title = None
        authors = []
        title_found = False
        
        for i, line in enumerate(lines[:20]):  # Check first 20 lines
            line = line.strip()
            if not line or len(line) < 3:
                continue
            
            if not title_found and len(line) > 10 and not any(kw in line.upper() for kw in self.section_keywords):
                title = line
                title_found = True
                continue
            
            # Check for common author patterns (emails, universities)
            if '@' in line or 'University' in line or 'Institute' in line:
                authors.append(line)
        
        # Process main content
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Skip very short lines (likely artifacts)
            if len(line) < 3:
                continue
            
            # Check if line is a section header
            is_section_header = False
            matched_keyword = None
            
            for keyword in self.section_keywords:
                # Exact match (case insensitive)
                if line.upper() == keyword:
                    is_section_header = True
                    matched_keyword = keyword
                    break
                
                # Numbered sections (e.g., "1. INTRODUCTION", "1 INTRODUCTION")
                if re.match(r'^\d+\.?\s+' + keyword + r'\s*$', line.upper()):
                    is_section_header = True
                    matched_keyword = keyword
                    break
            
            if is_section_header:
                # Save previous section
                if current_section:
                    sections.append({
                        'title': current_section,
                        'start': section_start_pos,
                        'end': len(content)
                    })
                
                current_section = matched_keyword.title()
                section_start_pos = len(content)
                content.append({'type': 'section', 'text': current_section})
            else:
                # Regular paragraph - only add if substantial
                if len(line) > 20 and not line.startswith('arXiv:'):  # Skip arxiv identifiers
                    content.append({'type': 'paragraph', 'text': line})
        
        # Add final section
        if current_section:
            sections.append({
                'title': current_section,
                'start': section_start_pos,
                'end': len(content)
            })
        
        return {
            'title': title,
            'authors': authors,
            'content': content,
            'sections': sections
        }
    
    def generate_html(self, paper_data, paper_id):
        """Generate single-column HTML from extracted paper data"""
        
        content_html = []
        
        # Add title
        if paper_data['title']:
            content_html.append(f'<h1 class="text-4xl font-bold mb-4">{paper_data["title"]}</h1>')
        
        # Add authors
        if paper_data['authors']:
            authors_text = '<br/>'.join(paper_data['authors'])
            content_html.append(f'<p class="text-gray-600 mb-8">{authors_text}</p>')
        
        # Add content
        for item in paper_data['content']:
            if item['type'] == 'section':
                content_html.append(f'<h2 class="text-2xl font-bold mb-4 mt-8">{item["text"]}</h2>')
            else:
                text = item['text'].strip()
                content_html.append(f'<p class="mb-4 text-justify">{text}</p>')
        
        # Generate section boundaries for tracking
        section_boundaries = {}
        scroll_height = 0
        increment = 600  # Approximate pixels per section
        
        for section in paper_data['sections']:
            section_boundaries[section['title']] = {
                'start': scroll_height,
                'end': scroll_height + increment
            }
            scroll_height += increment
        
        html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{paper_data['title'] or 'Academic Paper'}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 p-8">
    <!-- Paper ID: {paper_id} -->
    <div class="max-w-4xl mx-auto bg-white shadow-xl rounded-lg p-12">
        <div class="prose max-w-none">
            {''.join(content_html)}
        </div>
    </div>
    
    <div class="max-w-4xl mx-auto mt-8 p-6 bg-blue-50 rounded-lg">
        <h3 class="font-bold mb-2">✓ Review Checklist</h3>
        <ul class="text-sm space-y-1">
            <li>□ Title and authors correctly extracted</li>
            <li>□ All sections properly identified: {', '.join([s['title'] for s in paper_data['sections']])}</li>
            <li>□ Content is readable and well-formatted</li>
            <li>□ No major text extraction errors</li>
        </ul>
    </div>

    <script>
    // Section boundaries for {paper_id}
    const sectionBoundaries = {json.dumps(section_boundaries, indent=4)};
    
    console.log('Paper: {paper_id}');
    console.log('Sections:', {json.dumps([s['title'] for s in paper_data['sections']])});
    </script>
</body>
</html>
'''
        return html_template
    
    def convert(self, pdf_path, output_dir, paper_id=None):
        """Main conversion function"""
        pdf_path = Path(pdf_path)
        output_dir = Path(output_dir)
        
        # Generate paper ID from filename if not provided
        if not paper_id:
            paper_id = pdf_path.stem.lower().replace(' ', '-').replace('_', '-')
        
        print(f"\n{'='*60}")
        print(f"Processing: {pdf_path.name}")
        print(f"Paper ID: {paper_id}")
        print(f"{'='*60}")
        
        # Extract content
        paper_data = self.extract_pdf_content(str(pdf_path))
        
        print(f"\n📄 Title: {paper_data['title']}")
        print(f"👥 Authors: {len(paper_data['authors'])} found")
        print(f"📑 Sections: {len(paper_data['sections'])} detected")
        for section in paper_data['sections']:
            print(f"   - {section['title']}")
        
        # Generate HTML
        html = self.generate_html(paper_data, paper_id)
        
        # Save HTML
        html_path = output_dir / 'papers_html' / f"{paper_id}.html"
        html_path.parent.mkdir(parents=True, exist_ok=True)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        # Save metadata JSON
        metadata = {
            'paper_id': paper_id,
            'title': paper_data['title'],
            'authors': paper_data['authors'],
            'sections': paper_data['sections'],
            'source_pdf': pdf_path.name
        }
        
        json_path = output_dir / 'papers_json' / f"{paper_id}.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n✓ HTML saved: {html_path}")
        print(f"✓ Metadata saved: {json_path}")
        print(f"\n👉 Next: Open {html_path} in browser to review")
        print(f"{'='*60}\n")
        
        return html_path, json_path


def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_paper.py <pdf_file> [paper_id]")
        print("\nExample:")
        print("  python convert_paper.py ../papers/my_paper.pdf")
        print("  python convert_paper.py ../papers/my_paper.pdf custom-id")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    paper_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not Path(pdf_path).exists():
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)
    
    # Get project root directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    
    converter = PaperConverter()
    converter.convert(pdf_path, project_dir, paper_id)


if __name__ == "__main__":
    main()
