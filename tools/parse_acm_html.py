# #!/usr/bin/env python3
# """
# Parse ACM Digital Library saved HTML files
# Extracts clean content for reading experiments with actual section boundaries
# """

# import sys
# from pathlib import Path
# from bs4 import BeautifulSoup
# import json
# import re

# def parse_acm_html(html_path, paper_id):
#     """Parse ACM HTML and extract clean content"""
    
#     print(f"\n{'='*60}")
#     print(f"Parsing ACM HTML: {html_path.name}")
#     print(f"Paper ID: {paper_id}")
#     print(f"{'='*60}\n")
    
#     with open(html_path, 'r', encoding='utf-8') as f:
#         soup = BeautifulSoup(f.read(), 'html.parser')
    
#     # Find the main content wrapper
#     content_wrapper = soup.find('div', {'data-core-wrapper': 'content'})
    
#     if not content_wrapper:
#         print("❌ Could not find content wrapper")
#         return None
    
#     print("✓ Found content wrapper")
    
#     # Extract metadata
#     metadata = {
#         'paper_id': paper_id,
#         'title': '',
#         'authors': [],
#         'abstract': '',
#         'sections': []
#     }
    
#     # Title
#     title_tag = soup.find('title')
#     if title_tag:
#         title_text = title_tag.get_text()
#         title_text = title_text.split('|')[0].strip()
#         metadata['title'] = title_text
#         print(f"✓ Title: {title_text[:80]}...")
    
#     # Abstract
#     abstract_section = content_wrapper.find('section', {'id': 'summary-abstract'})
#     if abstract_section:
#         abstract_p = abstract_section.find('div', {'role': 'paragraph'})
#         if abstract_p:
#             metadata['abstract'] = abstract_p.get_text(strip=True)
#             # Add Abstract as a section
#             metadata['sections'].append({'title': 'Abstract'})
#             print(f"✓ Abstract: {len(metadata['abstract'])} characters")
    
#     # Main body
#     body_section = content_wrapper.find('section', {'id': 'bodymatter'})
    
#     content = []
#     images = []
    
#     if body_section:
#         print(f"✓ Found body content")
        
#         for element in body_section.find_all(['section', 'div', 'figure'], recursive=True):
#             # Section headers
#             if element.name == 'section' and element.get('id', '').startswith('sec-'):
#                 h2 = element.find('h2', recursive=False)
#                 if h2:
#                     section_title = h2.get_text(strip=True)
#                     metadata['sections'].append({'title': section_title})
#                     content.append({
#                         'type': 'section',
#                         'text': section_title
#                     })
#                     print(f"  📑 Section: {section_title}")
            
#             # Figures
#             elif element.name == 'figure':
#                 img = element.find('img')
#                 figcaption = element.find('figcaption')
                
#                 if img and img.get('src'):
#                     caption = figcaption.get_text(strip=True) if figcaption else ''
#                     img_src = img['src']
#                     img_filename = Path(img_src).name
                    
#                     images.append({
#                         'src': img_src,
#                         'filename': img_filename,
#                         'caption': caption
#                     })
                    
#                     content.append({
#                         'type': 'image',
#                         'src': img_src,
#                         'filename': img_filename,
#                         'caption': caption
#                     })
#                     print(f"  🖼️  Image: {img_filename}")
            
#             # Paragraphs
#             elif element.name == 'div' and element.get('role') == 'paragraph':
#                 text = element.get_text(strip=True)
#                 if len(text) > 30:
#                     content.append({
#                         'type': 'paragraph',
#                         'text': text
#                     })
    
#     print(f"\n✓ Extracted {len(content)} content items")
#     print(f"✓ Found {len(images)} images")
#     print(f"✓ Found {len(metadata['sections'])} sections")
    
#     return {
#         'metadata': metadata,
#         'content': content,
#         'images': images
#     }

# def calculate_section_boundaries(content, metadata):
#     """Calculate actual section boundaries based on content length"""
    
#     section_boundaries = {}
#     sections_list = []
#     current_section = None
#     section_start = 0
#     current_position = 0
    
#     # Title
#     if metadata['title']:
#         current_position += len(metadata['title']) * 2
    
#     # Abstract as first section
#     if metadata['abstract']:
#         sections_list.append({
#             'name': 'Abstract',
#             'start': current_position,
#             'content_length': len(metadata['abstract']) * 2 + 100
#         })
#         current_position += len(metadata['abstract']) * 2 + 100
    
#     # Process content to find sections and their lengths
#     for item in content:
#         if item['type'] == 'section':
#             # If there was a previous section, close it
#             if sections_list and 'end' not in sections_list[-1]:
#                 sections_list[-1]['end'] = current_position
            
#             # Start new section
#             sections_list.append({
#                 'name': item['text'],
#                 'start': current_position,
#                 'content_length': len(item['text']) * 2
#             })
#             current_position += len(item['text']) * 2
            
#         elif item['type'] == 'paragraph':
#             if sections_list:
#                 sections_list[-1]['content_length'] += len(item['text']) * 2
#             current_position += len(item['text']) * 2
            
#         elif item['type'] == 'image':
#             if sections_list:
#                 sections_list[-1]['content_length'] += 500
#             current_position += 500
    
#     # Close last section
#     if sections_list and 'end' not in sections_list[-1]:
#         sections_list[-1]['end'] = current_position
    
#     # Convert to final format
#     for section in sections_list:
#         if 'end' not in section:
#             section['end'] = section['start'] + section['content_length']
        
#         section_boundaries[section['name']] = {
#             'start': section['start'],
#             'end': section['end']
#         }
    
#     return section_boundaries

# def generate_clean_html(data, paper_id):
#     """Generate clean HTML for reading experiment"""
    
#     metadata = data['metadata']
#     content = data['content']
#     images = data['images']
    
#     content_html = []
    
#     # Title
#     if metadata['title']:
#         content_html.append(f'<h1 class="text-4xl font-bold mb-4">{metadata["title"]}</h1>')
    
#     # Abstract
#     if metadata['abstract']:
#         content_html.append('<h2 class="text-2xl font-bold mb-4 mt-8" data-section="Abstract">Abstract</h2>')
#         content_html.append(f'<p class="mb-4 text-justify">{metadata["abstract"]}</p>')
    
#     # Content
#     for item in content:
#         if item['type'] == 'section':
#             content_html.append(f'<h2 class="text-2xl font-bold mb-4 mt-8" data-section="{item["text"]}">{item["text"]}</h2>')
        
#         elif item['type'] == 'paragraph':
#             content_html.append(f'<p class="mb-4 text-justify">{item["text"]}</p>')
        
#         elif item['type'] == 'image':
#             img_relative = f"../papers_images/{paper_id}/{item['filename']}"
#             img_html = f'''<div class="my-8 p-4 bg-gray-50 rounded-lg">
#     <img src="{img_relative}" class="max-w-full mx-auto shadow-lg rounded" alt="{item['caption']}" />'''
#             if item['caption']:
#                 img_html += f'\n    <p class="text-sm text-gray-600 text-center mt-2 italic">{item["caption"]}</p>'
#             img_html += '\n</div>'
#             content_html.append(img_html)
    
#     # Calculate section boundaries
#     section_boundaries = calculate_section_boundaries(content, metadata)
    
#     # Add to metadata
#     metadata['section_boundaries'] = section_boundaries
    
#     print(f"\n📊 Section Boundaries:")
#     for section, bounds in section_boundaries.items():
#         length = bounds['end'] - bounds['start']
#         print(f"   {section}: chars {bounds['start']}-{bounds['end']} ({length} chars)")
    
#     html_template = f'''<!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>{metadata["title"]}</title>
#     <script src="https://cdn.tailwindcss.com"></script>
# </head>
# <body class="bg-gray-50 p-8">
#     <!-- Paper ID: {paper_id} -->
    
#     <div class="max-w-4xl mx-auto bg-white shadow-xl rounded-lg p-12">
#         <div class="prose max-w-none" id="paper-content">
#             {''.join(content_html)}
#         </div>
#     </div>
    
#     <div class="max-w-4xl mx-auto mt-8 p-6 bg-blue-50 rounded-lg">
#         <h3 class="font-bold mb-2">✓ Parsed Successfully</h3>
#         <ul class="text-sm space-y-1">
#             <li>□ Title: {metadata['title'][:50]}...</li>
#             <li>□ Sections: {', '.join([s['title'] for s in metadata['sections']])}</li>
#             <li>□ Images: {len(images)} found</li>
#         </ul>
#         <div class="mt-4 pt-4 border-t text-xs text-gray-600">
#             <strong>Next:</strong> Copy images from "_files" folder to papers_images/{paper_id}/
#         </div>
#     </div>

#     <script>
#     // Calculate scroll-based section boundaries on load
#     window.addEventListener('DOMContentLoaded', () => {{
#         const boundaries = {{}};
#         const sections = document.querySelectorAll('[data-section]');
#         const container = document.getElementById('paper-content');
        
#         sections.forEach((section, index) => {{
#             const name = section.getAttribute('data-section');
#             const start = section.offsetTop;
#             const end = (index < sections.length - 1) 
#                 ? sections[index + 1].offsetTop 
#                 : container.scrollHeight;
            
#             boundaries[name] = {{ start, end }};
#         }});
        
#         console.log('Section Boundaries (scroll pixels):', boundaries);
#         window.sectionBoundaries = boundaries;
#     }});
#     </script>
# </body>
# </html>
# '''
#     return html_template

# def main():
#     if len(sys.argv) < 2:
#         print("Usage: python parse_acm_html.py <html_file> [paper_id]")
#         print("\nExample:")
#         print("  python parse_acm_html.py downloaded_paper.html chi2025-lbw-01")
#         sys.exit(1)
    
#     html_path = Path(sys.argv[1])
#     paper_id = sys.argv[2] if len(sys.argv) > 2 else html_path.stem
    
#     if not html_path.exists():
#         print(f"Error: File not found: {html_path}")
#         sys.exit(1)
    
#     # Parse HTML
#     data = parse_acm_html(html_path, paper_id)
    
#     if not data:
#         print("Failed to parse HTML")
#         sys.exit(1)
    
#     # Generate clean HTML
#     clean_html = generate_clean_html(data, paper_id)
    
#     # Get project directory
#     script_dir = Path(__file__).parent
#     project_dir = script_dir.parent
    
#     # Save files
#     html_dir = project_dir / 'papers_html'
#     json_dir = project_dir / 'papers_json'
    
#     html_dir.mkdir(parents=True, exist_ok=True)
#     json_dir.mkdir(parents=True, exist_ok=True)
    
#     html_output = html_dir / f"{paper_id}.html"
#     json_output = json_dir / f"{paper_id}.json"
    
#     with open(html_output, 'w', encoding='utf-8') as f:
#         f.write(clean_html)
    
#     with open(json_output, 'w', encoding='utf-8') as f:
#         json.dump(data['metadata'], f, indent=2, ensure_ascii=False)
    
#     print(f"\n{'='*60}")
#     print(f"✅ HTML: {html_output}")
#     print(f"✅ JSON: {json_output} (includes section_boundaries)")
#     print(f"\n👉 Open {html_output} in browser to review")
#     print(f"{'='*60}\n")

# if __name__ == "__main__":
#     main()

#!/usr/bin/env python3
"""
Parse ACM Digital Library saved HTML files
Extracts clean content for reading experiments with actual section boundaries
"""

import sys
from pathlib import Path
from bs4 import BeautifulSoup
import json
import re

def parse_acm_html(html_path, paper_id):
    """Parse ACM HTML and extract clean content"""
    
    print(f"\n{'='*60}")
    print(f"Parsing ACM HTML: {html_path.name}")
    print(f"Paper ID: {paper_id}")
    print(f"{'='*60}\n")
    
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    # Find the main content wrapper
    content_wrapper = soup.find('div', {'data-core-wrapper': 'content'})
    
    if not content_wrapper:
        print("❌ Could not find content wrapper")
        return None
    
    print("✓ Found content wrapper")
    
    # Extract metadata
    metadata = {
        'paper_id': paper_id,
        'title': '',
        'authors': [],
        'abstract': '',
        'sections': []
    }
    
    # Title
    title_tag = soup.find('title')
    if title_tag:
        title_text = title_tag.get_text()
        title_text = title_text.split('|')[0].strip()
        metadata['title'] = title_text
        print(f"✓ Title: {title_text[:80]}...")
    
    # Abstract
    abstract_section = content_wrapper.find('section', {'id': 'summary-abstract'})
    if abstract_section:
        abstract_p = abstract_section.find('div', {'role': 'paragraph'})
        if abstract_p:
            metadata['abstract'] = abstract_p.get_text(strip=True)
            # Add Abstract as a section
            metadata['sections'].append({'title': 'Abstract'})
            print(f"✓ Abstract: {len(metadata['abstract'])} characters")
    
    # Main body
    body_section = content_wrapper.find('section', {'id': 'bodymatter'})
    
    content = []
    images = []
    tables = []
    
    if body_section:
        print(f"✓ Found body content")
        
        for element in body_section.find_all(['section', 'div', 'figure'], recursive=True):
            # Section headers (h2 for main sections)
            if element.name == 'section' and element.get('id', '').startswith('sec-'):
                h2 = element.find('h2', recursive=False)
                if h2:
                    section_title = h2.get_text(strip=True)
                    metadata['sections'].append({'title': section_title, 'level': 2})
                    content.append({
                        'type': 'section',
                        'text': section_title,
                        'level': 2
                    })
                    print(f"  📑 Section: {section_title}")

                # Subsection headers (h3)
                h3 = element.find('h3', recursive=False)
                if h3:
                    subsection_title = h3.get_text(strip=True)
                    metadata['sections'].append({'title': subsection_title, 'level': 3})
                    content.append({
                        'type': 'subsection',
                        'text': subsection_title,
                        'level': 3
                    })
                    print(f"    📑 Subsection: {subsection_title}")
            
            # Figures (images and tables)
            elif element.name == 'figure':
                # Check if it's a table
                table = element.find('table')
                if table:
                    figcaption = element.find('figcaption')
                    caption = figcaption.get_text(strip=True) if figcaption else ''
                    table_html = str(table)
                    
                    tables.append({
                        'caption': caption,
                        'html': table_html
                    })
                    
                    content.append({
                        'type': 'table',
                        'caption': caption,
                        'html': table_html
                    })
                    print(f"  📋 Table: {caption[:60]}...")
                
                # Check if it's an image
                else:
                    img = element.find('img')
                    if img and img.get('src'):
                        figcaption = element.find('figcaption')
                        caption = figcaption.get_text(strip=True) if figcaption else ''
                        img_src = img['src']
                        img_filename = Path(img_src).name
                        
                        images.append({
                            'src': img_src,
                            'filename': img_filename,
                            'caption': caption
                        })
                        
                        content.append({
                            'type': 'image',
                            'src': img_src,
                            'filename': img_filename,
                            'caption': caption
                        })
                        print(f"  🖼️  Image: {img_filename}")
            
            # Paragraphs
            elif element.name == 'div' and element.get('role') == 'paragraph':
                text = element.get_text(strip=True)
                if len(text) > 30:
                    content.append({
                        'type': 'paragraph',
                        'text': text
                    })
    
    print(f"\n✓ Extracted {len(content)} content items")
    print(f"✓ Found {len(images)} images")
    print(f"✓ Found {len(tables)} tables")
    print(f"✓ Found {len(metadata['sections'])} sections")
    
    return {
        'metadata': metadata,
        'content': content,
        'images': images,
        'tables': tables
    }

def calculate_section_boundaries(content, metadata):
    """Calculate actual section boundaries based on content length"""
    
    section_boundaries = {}
    sections_list = []
    current_section = None
    section_start = 0
    current_position = 0
    
    # Title
    if metadata['title']:
        current_position += len(metadata['title']) * 2
    
    # Abstract as first section
    if metadata['abstract']:
        sections_list.append({
            'name': 'Abstract',
            'start': current_position,
            'content_length': len(metadata['abstract']) * 2 + 100
        })
        current_position += len(metadata['abstract']) * 2 + 100
    
    # Process content to find sections and their lengths
    for item in content:
        if item['type'] == 'section' or item['type'] == 'subsection':
            # If there was a previous section, close it
            if sections_list and 'end' not in sections_list[-1]:
                sections_list[-1]['end'] = current_position

            # Start new section/subsection
            sections_list.append({
                'name': item['text'],
                'start': current_position,
                'content_length': len(item['text']) * 2
            })
            current_position += len(item['text']) * 2

        elif item['type'] == 'paragraph':
            if sections_list:
                sections_list[-1]['content_length'] += len(item['text']) * 2
            current_position += len(item['text']) * 2
            
        elif item['type'] == 'image':
            if sections_list:
                sections_list[-1]['content_length'] += 500
            current_position += 500
    
    # Close last section
    if sections_list and 'end' not in sections_list[-1]:
        sections_list[-1]['end'] = current_position
    
    # Convert to final format
    for section in sections_list:
        if 'end' not in section:
            section['end'] = section['start'] + section['content_length']
        
        section_boundaries[section['name']] = {
            'start': section['start'],
            'end': section['end']
        }
    
    return section_boundaries

def generate_clean_html(data, paper_id):
    """Generate clean HTML for reading experiment"""
    
    metadata = data['metadata']
    content = data['content']
    images = data['images']
    tables = data.get('tables', [])
    
    content_html = []
    
    # Title
    if metadata['title']:
        content_html.append(f'<h1 class="text-4xl font-bold mb-4">{metadata["title"]}</h1>')
    
    # Abstract
    if metadata['abstract']:
        content_html.append('<h2 class="text-2xl font-bold mb-4 mt-8" data-section="Abstract">Abstract</h2>')
        content_html.append(f'<p class="mb-4 text-justify">{metadata["abstract"]}</p>')
    
    # Content
    for item in content:
        if item['type'] == 'section':
            content_html.append(f'<h2 class="text-2xl font-bold mb-4 mt-8" data-section="{item["text"]}">{item["text"]}</h2>')

        elif item['type'] == 'subsection':
            content_html.append(f'<h3 class="text-xl font-semibold mb-3 mt-6" data-section="{item["text"]}">{item["text"]}</h3>')

        elif item['type'] == 'paragraph':
            content_html.append(f'<p class="mb-4 text-justify">{item["text"]}</p>')
        
        elif item['type'] == 'image':
            img_relative = f"../papers_images/{paper_id}/{item['filename']}"
            img_html = f'''<div class="my-8 p-4 bg-gray-50 rounded-lg">
    <img src="{img_relative}" class="max-w-full mx-auto shadow-lg rounded" alt="{item['caption']}" />'''
            if item['caption']:
                img_html += f'\n    <p class="text-sm text-gray-600 text-center mt-2 italic">{item["caption"]}</p>'
            img_html += '\n</div>'
            content_html.append(img_html)
        
        elif item['type'] == 'table':
            table_html = f'''<div class="my-8 overflow-x-auto">
    <div class="inline-block min-w-full align-middle">
        <div class="overflow-hidden border border-gray-300 rounded-lg">
            {item['html']}
        </div>'''
            if item['caption']:
                table_html += f'\n        <p class="text-sm text-gray-600 text-center mt-2 italic">{item["caption"]}</p>'
            table_html += '\n    </div>\n</div>'
            content_html.append(table_html)
    
    # Calculate section boundaries
    section_boundaries = calculate_section_boundaries(content, metadata)
    
    # Add to metadata
    metadata['section_boundaries'] = section_boundaries
    
    print(f"\n📊 Section Boundaries:")
    for section, bounds in section_boundaries.items():
        length = bounds['end'] - bounds['start']
        print(f"   {section}: chars {bounds['start']}-{bounds['end']} ({length} chars)")
    
    html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{metadata["title"]}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 p-8">
    <!-- Paper ID: {paper_id} -->
    
    <div class="max-w-4xl mx-auto bg-white shadow-xl rounded-lg p-12">
        <div class="prose max-w-none" id="paper-content">
            {''.join(content_html)}
        </div>
    </div>
    
    <div class="max-w-4xl mx-auto mt-8 p-6 bg-blue-50 rounded-lg">
        <h3 class="font-bold mb-2">✓ Parsed Successfully</h3>
        <ul class="text-sm space-y-1">
            <li>□ Title: {metadata['title'][:50]}...</li>
            <li>□ Sections: {', '.join([s['title'] for s in metadata['sections']])}</li>
            <li>□ Images: {len(images)} found</li>
        </ul>
        <div class="mt-4 pt-4 border-t text-xs text-gray-600">
            <strong>Next:</strong> Copy images from "_files" folder to papers_images/{paper_id}/
        </div>
    </div>

    <script>
    // Calculate scroll-based section boundaries on load
    window.addEventListener('DOMContentLoaded', () => {{
        const boundaries = {{}};
        const sections = document.querySelectorAll('[data-section]');
        const container = document.getElementById('paper-content');
        
        sections.forEach((section, index) => {{
            const name = section.getAttribute('data-section');
            const start = section.offsetTop;
            const end = (index < sections.length - 1) 
                ? sections[index + 1].offsetTop 
                : container.scrollHeight;
            
            boundaries[name] = {{ start, end }};
        }});
        
        console.log('Section Boundaries (scroll pixels):', boundaries);
        window.sectionBoundaries = boundaries;
    }});
    </script>
</body>
</html>
'''
    return html_template

def main():
    if len(sys.argv) < 2:
        print("Usage: python parse_acm_html.py <html_file> [paper_id]")
        print("\nExample:")
        print("  python parse_acm_html.py downloaded_paper.html chi2025-lbw-01")
        sys.exit(1)
    
    html_path = Path(sys.argv[1])
    paper_id = sys.argv[2] if len(sys.argv) > 2 else html_path.stem
    
    if not html_path.exists():
        print(f"Error: File not found: {html_path}")
        sys.exit(1)
    
    # Parse HTML
    data = parse_acm_html(html_path, paper_id)
    
    if not data:
        print("Failed to parse HTML")
        sys.exit(1)
    
    # Generate clean HTML
    clean_html = generate_clean_html(data, paper_id)
    
    # Get project directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    
    # Save files
    html_dir = project_dir / 'papers_html'
    json_dir = project_dir / 'papers_json'
    
    html_dir.mkdir(parents=True, exist_ok=True)
    json_dir.mkdir(parents=True, exist_ok=True)
    
    html_output = html_dir / f"{paper_id}.html"
    json_output = json_dir / f"{paper_id}.json"
    
    with open(html_output, 'w', encoding='utf-8') as f:
        f.write(clean_html)
    
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(data['metadata'], f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"✅ HTML: {html_output}")
    print(f"✅ JSON: {json_output} (includes section_boundaries)")
    print(f"\n👉 Open {html_output} in browser to review")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()