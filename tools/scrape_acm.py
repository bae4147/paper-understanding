#!/usr/bin/env python3
"""
ACM Digital Library HTML Scraper
Downloads HTML content and images from ACM DL papers for reading experiments
"""

import requests
from bs4 import BeautifulSoup
import json
import sys
import time
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

class ACMScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def extract_doi_from_url(self, url):
        """Extract DOI from ACM URL"""
        # Example: https://dl.acm.org/doi/10.1145/3706599.3719940
        match = re.search(r'doi/(10\.\d+/[\d.]+)', url)
        if match:
            return match.group(1)
        return None
    
    def scrape_paper(self, doi_or_url, output_dir, paper_id=None):
        """Scrape a paper from ACM Digital Library"""
        
        # Handle both DOI and full URL
        if doi_or_url.startswith('http'):
            doi = self.extract_doi_from_url(doi_or_url)
            url = doi_or_url
        else:
            doi = doi_or_url
            url = f'https://dl.acm.org/doi/{doi}'
        
        if not doi:
            print(f"❌ Could not extract DOI from: {doi_or_url}")
            return None
        
        if not paper_id:
            paper_id = doi.replace('/', '-').replace('.', '-')
        
        print(f"\n{'='*60}")
        print(f"Scraping ACM Paper")
        print(f"DOI: {doi}")
        print(f"URL: {url}")
        print(f"Paper ID: {paper_id}")
        print(f"{'='*60}\n")
        
        # Create output directories
        output_dir = Path(output_dir)
        html_dir = output_dir / 'papers_html'
        json_dir = output_dir / 'papers_json'
        img_dir = output_dir / 'papers_images' / paper_id
        
        html_dir.mkdir(parents=True, exist_ok=True)
        json_dir.mkdir(parents=True, exist_ok=True)
        img_dir.mkdir(parents=True, exist_ok=True)
        
        # Fetch the page
        print("📥 Fetching page...")
        try:
            response = self.session.get(url)
            response.raise_for_status()
        except Exception as e:
            print(f"❌ Error fetching page: {e}")
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract metadata
        print("📋 Extracting metadata...")
        metadata = self.extract_metadata(soup, doi, url)
        print(f"   Title: {metadata['title']}")
        print(f"   Authors: {len(metadata['authors'])} found")
        
        # Extract main content
        print("📄 Extracting content...")
        content = self.extract_content(soup, img_dir, url)
        
        # Generate clean HTML
        print("🎨 Generating HTML...")
        html = self.generate_html(metadata, content, paper_id, img_dir)
        
        # Save HTML
        html_path = html_dir / f'{paper_id}.html'
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        # Save metadata JSON
        json_path = json_dir / f'{paper_id}.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n✓ HTML saved: {html_path}")
        print(f"✓ Metadata saved: {json_path}")
        print(f"✓ Images saved: {img_dir}")
        print(f"\n👉 Next: Open {html_path} in browser to review")
        print(f"{'='*60}\n")
        
        return html_path, json_path
    
    def extract_metadata(self, soup, doi, url):
        """Extract paper metadata"""
        metadata = {
            'doi': doi,
            'url': url,
            'title': '',
            'authors': [],
            'abstract': '',
            'sections': [],
            'keywords': [],
            'publication': ''
        }
        
        # Title
        title_tag = soup.find('h1', class_='citation__title')
        if title_tag:
            metadata['title'] = title_tag.get_text(strip=True)
        
        # Authors
        authors_section = soup.find('div', class_='authors-section')
        if authors_section:
            author_tags = authors_section.find_all('a', class_='author-name')
            metadata['authors'] = [a.get_text(strip=True) for a in author_tags]
        
        # Abstract
        abstract_section = soup.find('div', class_='abstractSection')
        if abstract_section:
            abstract_p = abstract_section.find('p')
            if abstract_p:
                metadata['abstract'] = abstract_p.get_text(strip=True)
        
        # Sections
        section_headers = soup.find_all(['h2', 'h3'], class_=re.compile('section__title'))
        metadata['sections'] = [{'title': h.get_text(strip=True)} for h in section_headers]
        
        # Publication info
        pub_info = soup.find('div', class_='issue-item__detail')
        if pub_info:
            metadata['publication'] = pub_info.get_text(strip=True)
        
        return metadata
    
    def extract_content(self, soup, img_dir, base_url):
        """Extract main content including text and images"""
        content = []
        
        # Find main content area
        main_content = soup.find('div', class_='article__body')
        if not main_content:
            main_content = soup.find('div', class_='hlFld-Fulltext')
        
        if not main_content:
            print("   ⚠️ Could not find main content area")
            return content
        
        # Process all elements
        for element in main_content.find_all(['h2', 'h3', 'p', 'figure', 'img']):
            if element.name in ['h2', 'h3']:
                # Section header
                content.append({
                    'type': 'section',
                    'level': element.name,
                    'text': element.get_text(strip=True)
                })
            
            elif element.name == 'p':
                # Paragraph
                text = element.get_text(strip=True)
                if len(text) > 20:  # Only substantial paragraphs
                    content.append({
                        'type': 'paragraph',
                        'text': text
                    })
            
            elif element.name in ['figure', 'img']:
                # Image
                img_tag = element if element.name == 'img' else element.find('img')
                if img_tag and img_tag.get('src'):
                    img_url = urljoin(base_url, img_tag['src'])
                    img_filename = self.download_image(img_url, img_dir)
                    
                    if img_filename:
                        caption = ''
                        if element.name == 'figure':
                            caption_tag = element.find('figcaption')
                            if caption_tag:
                                caption = caption_tag.get_text(strip=True)
                        
                        content.append({
                            'type': 'image',
                            'src': f'../papers_images/{img_dir.name}/{img_filename}',
                            'caption': caption
                        })
        
        return content
    
    def download_image(self, url, img_dir):
        """Download an image"""
        try:
            # Get filename from URL
            filename = Path(urlparse(url).path).name
            if not filename:
                filename = f'image_{len(list(img_dir.glob("*")))}.png'
            
            filepath = img_dir / filename
            
            # Skip if already downloaded
            if filepath.exists():
                return filename
            
            # Download
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"   ✓ Downloaded image: {filename}")
            time.sleep(0.5)  # Be nice to the server
            return filename
            
        except Exception as e:
            print(f"   ⚠️ Failed to download image {url}: {e}")
            return None
    
    def generate_html(self, metadata, content, paper_id, img_dir):
        """Generate clean HTML for the paper"""
        
        # Generate content HTML
        content_html = []
        
        # Title
        content_html.append(f'<h1 class="text-4xl font-bold mb-4">{metadata["title"]}</h1>')
        
        # Authors
        if metadata['authors']:
            authors_html = ', '.join(metadata['authors'])
            content_html.append(f'<p class="text-gray-600 mb-2">{authors_html}</p>')
        
        # Publication
        if metadata['publication']:
            content_html.append(f'<p class="text-sm text-gray-500 mb-8">{metadata["publication"]}</p>')
        
        # Abstract
        if metadata['abstract']:
            content_html.append('<h2 class="text-2xl font-bold mb-4 mt-8">Abstract</h2>')
            content_html.append(f'<p class="mb-4 text-justify">{metadata["abstract"]}</p>')
        
        # Main content
        for item in content:
            if item['type'] == 'section':
                level = item['level']
                size_class = 'text-2xl' if level == 'h2' else 'text-xl'
                content_html.append(f'<{level} class="{size_class} font-bold mb-4 mt-8">{item["text"]}</{level}>')
            
            elif item['type'] == 'paragraph':
                content_html.append(f'<p class="mb-4 text-justify">{item["text"]}</p>')
            
            elif item['type'] == 'image':
                img_html = f'<div class="my-8"><img src="{item["src"]}" class="max-w-full mx-auto shadow-lg rounded" />'
                if item['caption']:
                    img_html += f'<p class="text-sm text-gray-600 text-center mt-2 italic">{item["caption"]}</p>'
                img_html += '</div>'
                content_html.append(img_html)
        
        # Generate section boundaries
        sections = [s['title'] for s in metadata['sections']]
        section_boundaries = {}
        for i, section in enumerate(sections):
            section_boundaries[section] = {
                'start': i * 600,
                'end': (i + 1) * 600
            }
        
        # Full HTML template
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
    <!-- Source: ACM Digital Library -->
    <!-- DOI: {metadata["doi"]} -->
    
    <div class="max-w-4xl mx-auto bg-white shadow-xl rounded-lg p-12">
        <div class="prose max-w-none">
            {''.join(content_html)}
        </div>
    </div>
    
    <div class="max-w-4xl mx-auto mt-8 p-6 bg-blue-50 rounded-lg">
        <h3 class="font-bold mb-2">✓ Review Checklist</h3>
        <ul class="text-sm space-y-1">
            <li>□ Title and authors correctly displayed</li>
            <li>□ All sections present: {', '.join(sections) if sections else 'Check manually'}</li>
            <li>□ Images loaded correctly</li>
            <li>□ Content is readable and well-formatted</li>
        </ul>
        <div class="mt-4 pt-4 border-t">
            <p class="text-xs text-gray-600">
                <strong>Source:</strong> ACM Digital Library<br/>
                <strong>DOI:</strong> <a href="{metadata['url']}" class="text-blue-600 hover:underline" target="_blank">{metadata['doi']}</a>
            </p>
        </div>
    </div>

    <script>
    // Section boundaries for {paper_id}
    const sectionBoundaries = {json.dumps(section_boundaries, indent=4)};
    
    console.log('Paper: {paper_id}');
    console.log('DOI: {metadata["doi"]}');
    console.log('Sections:', {json.dumps(sections)});
    </script>
</body>
</html>
'''
        return html_template


def main():
    if len(sys.argv) < 2:
        print("""
ACM Digital Library Scraper
===========================

Usage:
  python scrape_acm.py <DOI_or_URL> [paper_id]

Examples:
  python scrape_acm.py 10.1145/3706599.3719940
  python scrape_acm.py https://dl.acm.org/doi/10.1145/3706599.3719940
  python scrape_acm.py https://dl.acm.org/doi/10.1145/3706599.3719940 chi2025-lbw-01

Note:
  - Respects rate limits (adds delays between requests)
  - Downloads images to papers_images/ directory
  - Generates clean HTML for review
""")
        sys.exit(1)
    
    doi_or_url = sys.argv[1]
    paper_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Get project directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    
    scraper = ACMScraper()
    scraper.scrape_paper(doi_or_url, project_dir, paper_id)


if __name__ == "__main__":
    main()
