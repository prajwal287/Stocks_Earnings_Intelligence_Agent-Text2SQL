"""
Improved MD&A Extraction from 10-K PDFs (Version 2)

Uses pdfplumber for better text extraction and improved content detection.
Focuses on extracting actual MD&A narrative content, not headers.
"""

import os
import re
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False
    import PyPDF2

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PDF_FOLDER = '/Users/prajwalchambenandeeshappa/Github_Repos/Stocks_Earnings_Intelligence_Agent-Text2SQL/learning/sec_filings_pdf'

# MD&A detection patterns
MDA_START_PATTERNS = [
    r'Item\s+7[\.\s]+Management.*?Discussion.*?Analysis',
    r'Item\s+2[\.\s]+Management.*?Discussion.*?Analysis',  # For 10-Q
    r"Management's Discussion and Analysis",
]

MDA_END_PATTERNS = [
    r'Item\s+8[\.\s]+Financial',
    r'Item\s+3[\.\s]+Quantitative',  # For 10-Q
    r'FINANCIAL STATEMENTS',
    r'CONSOLIDATED BALANCE SHEET',
    r'CONSOLIDATED STATEMENTS OF',
]

# Subsection headers with improved detection
SUBSECTION_HEADERS = {
    'Results of Operations': [
        r'Results\s+of\s+Operations',
        r'Operating\s+Results',
        r'Performance\s+Analysis',
        r'Year-over-Year\s+Comparison',
        r'Comparison\s+of\s+Results',
    ],
    'Liquidity & Capital Resources': [
        r'Liquidity\s+and\s+Capital\s+Resources',
        r'Liquidity\s+Analysis',
        r'Cash\s+Flows?\s+(?:from|analysis)',
        r'Capital\s+Resources',
        r'Financing\s+Activities',
        r'Working\s+Capital',
    ],
    'Financial Condition': [
        r'Financial\s+Condition',
        r'Balance\s+Sheet\s+Analysis',
        r'Financial\s+Position',
        r'Assets?\s+and\s+Liabilities',
    ],
    'Risk Factors': [
        r'Risk\s+Factors?',
        r'Risks?\s+and\s+Uncertainties',
        r'Risk\s+Analysis',
        r'Critical\s+Risks?',
    ],
    'Critical Accounting': [
        r'Critical\s+Accounting\s+Policies',
        r'Accounting\s+Estimates',
        r'Estimates?\s+(?:and\s+)?Judgments?',
    ],
}

def extract_text_from_pdf_pdfplumber(pdf_path: str) -> str:
    """Extract text using pdfplumber (better for formatted documents)."""
    if not HAS_PDFPLUMBER:
        return ""

    try:
        text_parts = []
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    text_parts.append(text)

        return '\n'.join(text_parts)
    except Exception as e:
        logger.warning(f"pdfplumber extraction failed: {e}, falling back to PyPDF2")
        return ""

def extract_text_from_pdf_pypdf2(pdf_path: str) -> str:
    """Fallback: Extract text using PyPDF2."""
    try:
        import PyPDF2
        text_parts = []
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

        return '\n'.join(text_parts)
    except Exception as e:
        logger.error(f"PyPDF2 extraction failed: {e}")
        return ""

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from PDF file (try pdfplumber first, fallback to PyPDF2)."""
    if HAS_PDFPLUMBER:
        text = extract_text_from_pdf_pdfplumber(pdf_path)
        if len(text) > 10000:  # Good extraction
            return text

    return extract_text_from_pdf_pypdf2(pdf_path)

def is_likely_content(text: str, min_chars: int = 500) -> bool:
    """Check if text is likely actual content, not just headers."""
    if len(text) < min_chars:
        return False

    # Count sentences (rough indicator of content)
    sentences = re.split(r'[.!?]+', text)
    content_sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    # Content should have reasonable number of substantial sentences
    return len(content_sentences) > 10

def extract_mda_from_text(text: str) -> Optional[str]:
    """Extract MD&A section from 10-K/10-Q text with better validation."""
    if not text or len(text) < 5000:
        logger.warning(f"Text too short: {len(text)} chars")
        return None

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)

    # Strategy: Find "Item 7" followed by "Forward-Looking Statements"
    # This pattern is unique to the actual MD&A, not the TOC
    # We look for Item 7 that is NOT surrounded by other Item markers (which means TOC)

    start_idx = None

    # Find all Item 7 occurrences
    item7_matches = list(re.finditer(r'Item\s+7', text, re.IGNORECASE))

    for item7_match in item7_matches:
        pos = item7_match.start()
        # Get text after this Item 7
        text_after = text[pos:pos+2000]

        # Check if this is the real one by looking for "Forward-Looking Statements" nearby
        if re.search(r'Forward-Looking\s+Statements', text_after, re.IGNORECASE):
            # Also check that it's not immediately followed by Item 7A, 8, 9 (which would be TOC)
            immediate_after = text[pos:pos+300]
            if not re.search(r'Item\s+[78A][\.\s]', immediate_after[50:], re.IGNORECASE):
                start_idx = pos
                logger.info(f"   ✓ Found real MD&A (Item 7 with Forward-Looking Statements)")
                break

    if start_idx is None:
        # Fallback: use last Item 7 occurrence
        if item7_matches:
            start_idx = item7_matches[-1].start()
            logger.info(f"   ✓ Using fallback (last Item 7)")
        else:
            logger.warning("Could not find MD&A start marker")
            return None

    logger.info(f"   MD&A starts at position {start_idx}")

    # Find MD&A end
    end_idx = None
    search_text = text[start_idx:]
    for pattern in MDA_END_PATTERNS:
        match = re.search(pattern, search_text, re.IGNORECASE)
        if match:
            end_idx = start_idx + match.start()
            break

    if end_idx is None:
        # Default to next 500KB of text if no end marker found
        end_idx = min(start_idx + 500000, len(text))

    mda_text = text[start_idx:end_idx].strip()

    # Validate that we got actual content
    if not is_likely_content(mda_text):
        logger.warning(f"Extracted text may not be valid content: {len(mda_text)} chars")
        return None

    logger.info(f"   ✅ Extracted {len(mda_text):,} characters of MD&A content")

    # Count approximate paragraphs
    paragraphs = [p.strip() for p in mda_text.split('\n') if len(p.strip()) > 50]
    logger.info(f"   📊 Contains ~{len(paragraphs)} substantial paragraphs")

    return mda_text

def split_mda_by_subsection(mda_text: str) -> Dict[str, str]:
    """Split MD&A into subsections with improved detection."""
    subsections = {}

    for subsection_name, patterns in SUBSECTION_HEADERS.items():
        best_match = None
        best_pos = len(mda_text)

        # Find the first occurrence of any pattern for this subsection
        for pattern in patterns:
            match = re.search(pattern, mda_text, re.IGNORECASE)
            if match and match.start() < best_pos:
                best_match = match
                best_pos = match.start()

        if best_match:
            start = best_match.start()

            # Find the next subsection header
            end = len(mda_text)
            for other_name, other_patterns in SUBSECTION_HEADERS.items():
                if other_name == subsection_name:
                    continue

                for other_pattern in other_patterns:
                    # Search after current position
                    other_match = re.search(other_pattern, mda_text[start+50:], re.IGNORECASE)
                    if other_match:
                        candidate_end = start + 50 + other_match.start()
                        if candidate_end < end:
                            end = candidate_end

            subsection_text = mda_text[start:end].strip()

            # Only include substantial subsections
            if len(subsection_text) > 200 and is_likely_content(subsection_text, min_chars=200):
                subsections[subsection_name] = subsection_text
                logger.info(f"      ✓ {subsection_name}: {len(subsection_text):,} chars")

    if not subsections:
        # Fallback: treat entire MD&A as single section
        if is_likely_content(mda_text, min_chars=500):
            subsections["General MD&A"] = mda_text
            logger.info(f"      ✓ General MD&A: {len(mda_text):,} chars")

    return subsections

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks at sentence boundaries."""
    if not text or len(text) < 100:
        return [text] if text and len(text) > 50 else []

    chunks = []
    start = 0
    max_iterations = len(text) // (chunk_size - overlap) + 100  # Safety limit

    while start < len(text) and len(chunks) < max_iterations:
        end = min(start + chunk_size, len(text))

        # Try to break at sentence boundary (look backwards from end)
        if end < len(text):
            search_chunk = text[start:end]
            last_period = search_chunk.rfind('.')

            if last_period > chunk_size * 0.5:  # At least halfway through
                end = start + last_period + 1

        chunk = text[start:end].strip()
        if len(chunk) > 50:  # Only keep substantial chunks
            chunks.append(chunk)

        start = end - overlap
        if start >= len(text):
            break

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
    """Process single 10-K PDF with improved extraction."""
    filename = os.path.basename(pdf_path)
    ticker, year = parse_filename(filename)

    if not ticker:
        logger.warning(f"Could not parse filename: {filename}")
        return None

    logger.info(f"\n{'='*70}")
    logger.info(f"📄 Processing: {ticker} {year}")
    logger.info(f"{'='*70}")

    logger.info(f"   1️⃣  Reading PDF...")
    text = extract_text_from_pdf(pdf_path)
    if not text or len(text) < 5000:
        logger.error(f"   ❌ Failed to extract text from PDF (got {len(text)} chars)")
        return None

    logger.info(f"   ✅ Total text: {len(text):,} characters")

    logger.info(f"   2️⃣  Extracting MD&A section...")
    mda_text = extract_mda_from_text(text)
    if not mda_text:
        logger.error("   ❌ Could not extract MD&A section")
        return None

    logger.info(f"   3️⃣  Detecting subsections...")
    subsections = split_mda_by_subsection(mda_text)
    if not subsections:
        logger.error("   ❌ No subsections extracted")
        return None

    logger.info(f"   ✅ Found {len(subsections)} subsections")

    logger.info(f"   4️⃣  Chunking text by subsection...")
    all_chunks = []
    for subsection_name, subsection_text in subsections.items():
        chunks = chunk_text(subsection_text, chunk_size=1000, overlap=100)
        for chunk in chunks:
            all_chunks.append({
                'text': chunk,
                'subsection': subsection_name,
                'length': len(chunk)
            })

        logger.info(f"      {subsection_name}: {len(chunks)} chunks")

    if not all_chunks:
        logger.error("   ❌ Failed to create chunks")
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

    logger.info(f"   ✅ SUCCESS! Extracted {len(all_chunks)} chunks from {len(mda_text):,} chars")

    # Show breakdown
    breakdown = {}
    for chunk in all_chunks:
        subsection = chunk['subsection']
        breakdown[subsection] = breakdown.get(subsection, 0) + 1

    for subsection, count in sorted(breakdown.items(), key=lambda x: x[1], reverse=True):
        logger.info(f"      • {subsection}: {count} chunks")

    return result

def process_all_pdfs() -> List[Dict]:
    """Process all 10-K PDFs in folder."""
    if not os.path.exists(PDF_FOLDER):
        logger.error(f"PDF folder not found: {PDF_FOLDER}")
        return []

    pdf_files = sorted([f for f in os.listdir(PDF_FOLDER) if f.endswith('.pdf')])

    logger.info(f"\n{'='*70}")
    logger.info(f"🚀 PHASE 2B: Improved MD&A Extraction (V2)")
    logger.info(f"{'='*70}")
    logger.info(f"📦 Found {len(pdf_files)} PDF files")
    if HAS_PDFPLUMBER:
        logger.info(f"📚 Using pdfplumber for better text extraction")
    else:
        logger.info(f"📚 Using PyPDF2 for text extraction")
    logger.info(f"{'='*70}\n")

    results = []
    successful = 0
    failed = 0

    for i, pdf_file in enumerate(pdf_files, 1):
        pdf_path = os.path.join(PDF_FOLDER, pdf_file)
        logger.info(f"[{i}/{len(pdf_files)}] {pdf_file}")

        result = process_pdf_file(pdf_path)
        if result:
            results.append(result)
            successful += 1
        else:
            failed += 1

    logger.info(f"\n{'='*70}")
    logger.info(f"📊 SUMMARY")
    logger.info(f"{'='*70}")
    logger.info(f"✅ Successful: {successful}/{len(pdf_files)}")
    logger.info(f"❌ Failed: {failed}/{len(pdf_files)}")

    total_chunks = sum(r['chunk_count'] for r in results)
    total_chars = sum(r['text_length'] for r in results)
    logger.info(f"📈 Total chunks: {total_chunks}")
    logger.info(f"📈 Total characters: {total_chars:,}")
    logger.info(f"{'='*70}\n")

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
