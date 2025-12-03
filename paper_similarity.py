#!/usr/bin/env python3
"""
CHI LBW Paper Pair Selection Pipeline
=====================================
Selects the most semantically distant paper pair from a set of HCI papers
using SPECTER2 embeddings for stimulus selection diversity.
"""

import os
import re
import fitz  # PyMuPDF
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple, List, Dict, Optional
import warnings
warnings.filterwarnings('ignore')


def extract_title_abstract_from_pdf(pdf_path: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract title and abstract from an ACM-formatted PDF.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Tuple of (title, abstract) or (None, None) if extraction fails
    """
    try:
        doc = fitz.open(pdf_path)

        # Get text from first page (title and abstract are typically there)
        first_page = doc[0]
        text = first_page.get_text()

        # Also get text blocks with font info for better title detection
        blocks = first_page.get_text("dict")["blocks"]

        # Extract title - usually the largest font text at the top
        title = None
        max_font_size = 0
        title_candidates = []

        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        font_size = span["size"]
                        text_content = span["text"].strip()
                        if font_size > 12 and len(text_content) > 5:
                            title_candidates.append((font_size, text_content, block["bbox"][1]))

        # Sort by font size (descending) and y-position (ascending)
        title_candidates.sort(key=lambda x: (-x[0], x[1]))

        # Get title from largest font near the top
        if title_candidates:
            # Combine multiple spans that might form the title
            largest_size = title_candidates[0][0]
            title_parts = [t[1] for t in title_candidates if t[0] >= largest_size - 1]
            title = " ".join(title_parts[:3])  # Usually title is in first few large text blocks

        # Extract abstract
        abstract = None
        full_text = ""
        for page_num in range(min(2, len(doc))):  # Check first 2 pages
            full_text += doc[page_num].get_text()

        # Common patterns for abstract in ACM papers
        abstract_patterns = [
            r'ABSTRACT\s*\n(.*?)(?=\n\s*(?:CCS CONCEPTS|KEYWORDS|ACM Reference|1\s+INTRODUCTION|1\.|Author Keywords))',
            r'Abstract\s*\n(.*?)(?=\n\s*(?:CCS Concepts|Keywords|ACM Reference|1\s+Introduction|1\.|Author Keywords))',
            r'ABSTRACT[:\s]*(.*?)(?=CCS CONCEPTS|KEYWORDS|1\s+INTRODUCTION)',
        ]

        for pattern in abstract_patterns:
            match = re.search(pattern, full_text, re.DOTALL | re.IGNORECASE)
            if match:
                abstract = match.group(1).strip()
                # Clean up the abstract
                abstract = re.sub(r'\s+', ' ', abstract)
                abstract = abstract.strip()
                if len(abstract) > 50:  # Sanity check
                    break

        doc.close()

        # Clean up title
        if title:
            title = re.sub(r'\s+', ' ', title).strip()

        return title, abstract

    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return None, None


def load_specter2_model():
    """
    Load SPECTER2 model with proximity adapter for semantic distance measurement.

    Returns:
        Tuple of (tokenizer, model)
    """
    from transformers import AutoTokenizer, AutoModel
    from adapters import AutoAdapterModel

    print("Loading SPECTER2 model with proximity adapter...")

    # Load base model with adapter support
    tokenizer = AutoTokenizer.from_pretrained("allenai/specter2_base")
    model = AutoAdapterModel.from_pretrained("allenai/specter2_base")

    # Load and activate proximity adapter (for semantic distance)
    model.load_adapter("allenai/specter2", source="hf", load_as="proximity", set_active=True)

    print("Model loaded successfully!")
    return tokenizer, model


def get_embeddings(texts: List[str], tokenizer, model) -> np.ndarray:
    """
    Generate SPECTER2 embeddings for a list of texts.

    Args:
        texts: List of "{title} [SEP] {abstract}" formatted strings
        tokenizer: SPECTER2 tokenizer
        model: SPECTER2 model with proximity adapter

    Returns:
        numpy array of embeddings (n_texts, embedding_dim)
    """
    import torch

    embeddings = []

    for text in texts:
        inputs = tokenizer(
            text,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )

        with torch.no_grad():
            outputs = model(**inputs)
            # Use CLS token embedding
            embedding = outputs.last_hidden_state[:, 0, :].numpy()
            embeddings.append(embedding[0])

    return np.array(embeddings)


def compute_pairwise_distances(embeddings: np.ndarray) -> np.ndarray:
    """
    Compute pairwise cosine distances between all embeddings.

    Args:
        embeddings: numpy array of shape (n_samples, embedding_dim)

    Returns:
        Distance matrix of shape (n_samples, n_samples)
    """
    from sklearn.metrics.pairwise import cosine_distances

    return cosine_distances(embeddings)


def find_max_distance_pair(distance_matrix: np.ndarray, paper_names: List[str]) -> Tuple[str, str, float]:
    """
    Find the pair of papers with maximum semantic distance.

    Args:
        distance_matrix: Pairwise distance matrix
        paper_names: List of paper identifiers

    Returns:
        Tuple of (paper1, paper2, distance)
    """
    # Set diagonal to -inf to exclude self-comparisons
    np.fill_diagonal(distance_matrix, -np.inf)

    # Find maximum
    max_idx = np.unravel_index(np.argmax(distance_matrix), distance_matrix.shape)
    max_distance = distance_matrix[max_idx]

    return paper_names[max_idx[0]], paper_names[max_idx[1]], max_distance


def create_visualization(distance_matrix: np.ndarray, paper_names: List[str], output_dir: str):
    """
    Create visualizations: heatmap and t-SNE/MDS plot.

    Args:
        distance_matrix: Pairwise distance matrix
        paper_names: List of paper identifiers
        output_dir: Directory to save visualizations
    """
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn.manifold import MDS

    # Short names for visualization
    short_names = [name[:20] + "..." if len(name) > 20 else name for name in paper_names]

    # 1. Heatmap
    plt.figure(figsize=(14, 12))
    sns.heatmap(
        distance_matrix,
        xticklabels=short_names,
        yticklabels=short_names,
        cmap='RdYlBu_r',
        annot=True,
        fmt='.2f',
        square=True
    )
    plt.title('Pairwise Semantic Distance (Cosine Distance)\nSPECTER2 with Proximity Adapter', fontsize=14)
    plt.xticks(rotation=45, ha='right', fontsize=8)
    plt.yticks(rotation=0, fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'distance_heatmap.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: distance_heatmap.png")

    # 2. MDS visualization
    mds = MDS(n_components=2, dissimilarity='precomputed', random_state=42, normalized_stress='auto')
    coords = mds.fit_transform(distance_matrix)

    plt.figure(figsize=(12, 10))
    plt.scatter(coords[:, 0], coords[:, 1], s=100, c='steelblue', alpha=0.7)

    for i, name in enumerate(short_names):
        plt.annotate(
            name,
            (coords[i, 0], coords[i, 1]),
            xytext=(5, 5),
            textcoords='offset points',
            fontsize=8,
            alpha=0.8
        )

    plt.title('MDS Visualization of Paper Semantic Space\nSPECTER2 Embeddings', fontsize=14)
    plt.xlabel('MDS Dimension 1')
    plt.ylabel('MDS Dimension 2')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'mds_visualization.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: mds_visualization.png")


def main():
    """Main pipeline execution."""

    # Configuration
    PDF_DIR = "./pdfs"
    OUTPUT_DIR = "./output"

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Step 1: Extract title and abstract from all PDFs
    print("\n" + "="*60)
    print("Step 1: Extracting titles and abstracts from PDFs")
    print("="*60)

    pdf_files = sorted(Path(PDF_DIR).glob("*.pdf"))
    papers = {}

    for pdf_path in pdf_files:
        print(f"\nProcessing: {pdf_path.name}")
        title, abstract = extract_title_abstract_from_pdf(str(pdf_path))

        if title and abstract:
            papers[pdf_path.stem] = {
                'filename': pdf_path.name,
                'title': title,
                'abstract': abstract,
                'specter_input': f"{title} [SEP] {abstract}"
            }
            print(f"  Title: {title[:60]}...")
            print(f"  Abstract: {abstract[:100]}...")
        else:
            print(f"  Warning: Could not extract title/abstract")

    print(f"\nSuccessfully processed {len(papers)} papers")

    if len(papers) < 2:
        print("Error: Need at least 2 papers to compute distances")
        return

    # Save extracted data
    papers_df = pd.DataFrame.from_dict(papers, orient='index')
    papers_df.to_csv(os.path.join(OUTPUT_DIR, 'extracted_papers.csv'))
    print(f"Saved: extracted_papers.csv")

    # Step 2: Generate SPECTER2 embeddings
    print("\n" + "="*60)
    print("Step 2: Generating SPECTER2 embeddings")
    print("="*60)

    tokenizer, model = load_specter2_model()

    paper_ids = list(papers.keys())
    texts = [papers[pid]['specter_input'] for pid in paper_ids]

    embeddings = get_embeddings(texts, tokenizer, model)
    print(f"Generated embeddings: {embeddings.shape}")

    # Save embeddings
    embeddings_df = pd.DataFrame(embeddings, index=paper_ids)
    embeddings_df.to_csv(os.path.join(OUTPUT_DIR, 'embeddings.csv'))
    print(f"Saved: embeddings.csv")

    # Step 3: Compute pairwise distances
    print("\n" + "="*60)
    print("Step 3: Computing pairwise cosine distances")
    print("="*60)

    distance_matrix = compute_pairwise_distances(embeddings)

    # Save distance matrix
    distance_df = pd.DataFrame(distance_matrix, index=paper_ids, columns=paper_ids)
    distance_df.to_csv(os.path.join(OUTPUT_DIR, 'distance_matrix.csv'))
    print(f"Saved: distance_matrix.csv")

    # Step 4: Find maximum distance pair
    print("\n" + "="*60)
    print("Step 4: Finding maximum distance pair")
    print("="*60)

    # Use titles for readable output
    paper_titles = [papers[pid]['title'] for pid in paper_ids]
    paper1, paper2, max_dist = find_max_distance_pair(distance_matrix.copy(), paper_titles)

    print(f"\n{'*'*60}")
    print("MOST SEMANTICALLY DISTANT PAPER PAIR")
    print('*'*60)
    print(f"\nPaper 1: {paper1}")
    print(f"\nPaper 2: {paper2}")
    print(f"\nCosine Distance: {max_dist:.4f}")
    print('*'*60)

    # Also find by file ID
    id1, id2, _ = find_max_distance_pair(distance_matrix.copy(), paper_ids)

    # Save result
    result = {
        'paper1_id': id1,
        'paper1_title': papers[id1]['title'],
        'paper2_id': id2,
        'paper2_title': papers[id2]['title'],
        'cosine_distance': max_dist
    }

    result_df = pd.DataFrame([result])
    result_df.to_csv(os.path.join(OUTPUT_DIR, 'max_distance_pair.csv'), index=False)
    print(f"\nSaved: max_distance_pair.csv")

    # Step 5: Create visualizations
    print("\n" + "="*60)
    print("Step 5: Creating visualizations")
    print("="*60)

    # Use short titles for visualization
    short_titles = [t[:25] + "..." if len(t) > 25 else t for t in paper_titles]
    create_visualization(distance_matrix, short_titles, OUTPUT_DIR)

    print("\n" + "="*60)
    print("Pipeline completed successfully!")
    print("="*60)
    print(f"\nOutput files in: {OUTPUT_DIR}/")
    print("  - extracted_papers.csv (title, abstract for each paper)")
    print("  - embeddings.csv (SPECTER2 embeddings)")
    print("  - distance_matrix.csv (pairwise cosine distances)")
    print("  - max_distance_pair.csv (most distant pair)")
    print("  - distance_heatmap.png (visualization)")
    print("  - mds_visualization.png (2D projection)")


if __name__ == "__main__":
    main()
