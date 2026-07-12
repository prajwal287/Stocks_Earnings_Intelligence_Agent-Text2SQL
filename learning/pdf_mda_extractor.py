"""
Extract & Categorize MD&A from local 10-K PDF files for Text2SQL Agent

This module:
1. Reads 10-K PDFs from sec_filings_pdf/ folder
2. Extracts Management Discussion & Analysis (MD&A)
3. Detects and tags subsections (Results, Liquidity, Risks, etc.)
4. Chunks text by subsection for precise RAG retrieval
5. Returns structured data ready for PostgreSQL loading
"""

import PyPDF2
import os
import logging
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PDF_FOLDER = '/Users/prajwalchambenandeeshappa/Github_Repos/Stocks_Earnings_Intelligence_Agent-Text2SQL/learning/sec_filings_pdf'

# MD&A section markers in 10-K documents
MDA_START_PATTERNS = [
    r'Item\s+7[\.\s]+Management.*?Discussion.*?Analysis',
    r"MD&A",
    r"Management's Discussion and Analysis"
]

MDA_END_PATTERNS = [
    r'Item\s+8[\.\s]+Financial',
    r'Item\s+8[\.\s]+Quantitative',
    r'FINANCIAL STATEMENTS',
    r'CONSOLIDATED BALANCE SHEET'
]

# MD&A Subsection patterns
SUBSECTION_PATTERNS = {
    'Results of Operations': [
        r'Results\s+of\s+Operations',
        r'Operating\s+Results',
        r'Performance',
    ],
    'Financial Condition': [
        r'Financial\s+Condition',
        r'Balance\s+Sheet',
        r'Assets?\s+and\s+Liabilities',
    ],
    'Liquidity & Capital Resources': [
        r'Liquidity\s+and\s+Capital',
        r'Cash\s+Flows?',
        r'Capital\s+Resources',
        r'Financing\s+Activities',
    ],
    'Risk Factors': [
        r'Risk\s+Factors?',
        r'Risks?\s+and\s+Uncertainties',
        r'Critical\s+Risks?',
    ],
    'Critical Accounting': [
        r'Critical\s+Accounting\s+Policies',
        r'Accounting\s+Estimates',
        r'Estimates\s+and\s+Judgments',
    ],
}


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from PDF file."""
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ''
            for page in reader.pages:
                text += page.extract_text() + '\n'
        return text
    except Exception as e:
        logger.error(f"Error reading PDF {pdf_path}: {e}")
        return ""


def extract_mda_from_text(text: str) -> Optional[str]:
    """Extract MD&A section from 10-K text."""
    if not text:
        return None

    text = re.sub(r'\s+', ' ', text)

    start_idx = None
    for pattern in MDA_START_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            start_idx = match.start()
            break

    if start_idx is None:
        logger.warning("Could not find MD&A start marker")
        return None

    end_idx = None
    search_text = text[start_idx:]
    for pattern in MDA_END_PATTERNS:
        match = re.search(pattern, search_text, re.IGNORECASE)
        if match:
            end_idx = start_idx + match.start()
            break

    if end_idx is None:
        end_idx = start_idx + 500000

    mda_text = text[start_idx:end_idx].strip()
    logger.info(f"   Extracted {len(mda_text):,} characters of MD&A")
    return mda_text


def split_mda_by_subsection(mda_text: str) -> Dict[str, str]:
    """Split MD&A into subsections."""
    subsections = {}

    for subsection_name, patterns in SUBSECTION_PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, mda_text, re.IGNORECASE)
            if match:
                start = match.start()
                # Find next subsection
                end = len(mda_text)
                for other_name, other_patterns in SUBSECTION_PATTERNS.items():
                    if other_name == subsection_name:
                        continue
                    for other_pattern in other_patterns:
                        other_match = re.search(other_pattern, mda_text[start+100:], re.IGNORECASE)
                        if other_match:
                            candidate_end = start + 100 + other_match.start()
                            if candidate_end < end:
                                end = candidate_end

                subsection_text = mda_text[start:end].strip()
                if len(subsection_text) > 100:
                    subsections[subsection_name] = subsection_text
                break

    if not subsections:
        subsections["General MD&A"] = mda_text

    return subsections


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks at sentence boundaries."""
    if not text or len(text) < chunk_size:
        return [text] if text else []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]

        if end < len(text):
            last_period = chunk.rfind('.')
            if last_period > chunk_size * 0.7:
                end = start + last_period + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks


def parse_filename(filename: str) -> Tuple[str, str]:
    """Parse ticker and year from filename like 'aapl-20211231.pdf'"""
    base = filename.replace('.pdf', '')
    parts = base.rsplit('-', 1)

    if len(parts) == 2:
        ticker = parts[0].upper()
        date_str = parts[1]
        year = date_str[:4]
        return ticker, year
    return "", ""


def process_pdf_file(pdf_path: str) -> Optional[Dict]:
    """Process single 10-K PDF and extract categorized MD&A."""
    filename = os.path.basename(pdf_path)
    ticker, year = parse_filename(filename)

    if not ticker:
        logger.warning(f"Could not parse filename: {filename}")
        return None

    logger.info(f"\n{'='*70}")
    logger.info(f"📄 Processing: {ticker} {year}")
    logger.info(f"{'='*70}")

    logger.info(f"   Reading PDF...")
    text = extract_text_from_pdf(pdf_path)
    if not text:
        logger.error("   Failed to extract text from PDF")
        return None

    logger.info(f"   Total text: {len(text):,} characters")

    logger.info(f"   Extracting MD&A...")
    mda_text = extract_mda_from_text(text)
    if not mda_text:
        logger.error("   Could not extract MD&A section")
        return None

    logger.info(f"   Detecting subsections...")
    subsections = split_mda_by_subsection(mda_text)
    logger.info(f"   Found {len(subsections)} subsections: {', '.join(subsections.keys())}")

    logger.info(f"   Chunking text by subsection...")
    all_chunks = []
    for subsection_name, subsection_text in subsections.items():
        chunks = chunk_text(subsection_text, chunk_size=1000, overlap=100)
        for chunk in chunks:
            all_chunks.append({
                'text': chunk,
                'subsection': subsection_name,
                'length': len(chunk)
            })

    if not all_chunks:
        logger.error("   Failed to create chunks")
        return None

    result = {
        "ticker": ticker,
        "year": year,
        "filename": filename,
        "pdf_path": pdf_path,
        "mda_text": mda_text,
        "subsections": subsections,
        "chunks": all_chunks,
        "chunk_count": len(all_chunks),
        "text_length": len(mda_text),
        "extracted_at": datetime.now().isoformat(),
    }

    logger.info(f"✅ Success! Extracted {len(all_chunks)} chunks from {len(mda_text):,} characters")
    subsection_breakdown = ', '.join([f'{s}({sum(1 for c in all_chunks if c["subsection"]==s)})' for s in subsections.keys()])
    logger.info(f"   Subsection breakdown: {subsection_breakdown}")
    return result


def process_all_pdfs() -> List[Dict]:
    """Process all 10-K PDFs in folder."""
    if not os.path.exists(PDF_FOLDER):
        logger.error(f"PDF folder not found: {PDF_FOLDER}")
        return []

    pdf_files = sorted([f for f in os.listdir(PDF_FOLDER) if f.endswith('.pdf')])
    logger.info(f"\n🚀 PHASE 2B: PDF MD&A Extraction (with Subsection Detection)")
    logger.info(f"Found {len(pdf_files)} PDF files\n")

    results = []
    for i, pdf_file in enumerate(pdf_files, 1):
        pdf_path = os.path.join(PDF_FOLDER, pdf_file)
        logger.info(f"[{i}/{len(pdf_files)}] {pdf_file}")

        result = process_pdf_file(pdf_path)
        if result:
            results.append(result)

    logger.info(f"\n{'='*70}")
    logger.info(f"✅ Processed {len(results)}/{len(pdf_files)} PDFs successfully")
    logger.info(f"{'='*70}")

    return results


def prepare_chunks_for_dlt(filing_data: Dict) -> List[Dict]:
    """Transform chunks into format ready for dlt loading."""
    chunks_for_load = []

    for chunk_id, chunk_info in enumerate(filing_data['chunks'], 1):
        chunk_record = {
            "ticker": filing_data['ticker'],
            "year": filing_data['year'],
            "filename": filing_data['filename'],
            "section": chunk_info['subsection'],
            "chunk_id": chunk_id,
            "text": chunk_info['text'],
            "text_length": chunk_info['length'],
            "extracted_at": filing_data['extracted_at'],
        }
        chunks_for_load.append(chunk_record)

    return chunks_for_load


if __name__ == "__main__":
    results = process_all_pdfs()
    total_chunks = sum(r['chunk_count'] for r in results)
    print(f"\n✅ Ready to load {total_chunks} chunks to PostgreSQL")
