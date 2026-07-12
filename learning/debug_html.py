# Add this cell AFTER Step 2 (after you get HTML)

if html:
    print("=" * 60)
    print("DEBUG: Analyzing HTML Structure")
    print("=" * 60)
    
    # Clean HTML
    cleaned = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    cleaned = re.sub(r'<style[^>]*>.*?</style>', '', cleaned, flags=re.DOTALL)
    
    soup = BeautifulSoup(cleaned, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)
    text_lower = text.lower()
    
    print(f"\nTotal text length: {len(text)} chars")
    print(f"\nFirst 1000 chars:\n{text[:1000]}")
    print("\n" + "=" * 60)
    print("Looking for markers...")
    print("=" * 60)
    
    markers = [
        "item 2.",
        "management's discussion",
        "management discussion",
        "md&a",
        "results of operations",
        "liquidity",
        "capital resources",
        "item 3",
        "quantitative",
    ]
    
    for marker in markers:
        idx = text_lower.find(marker)
        if idx != -1:
            print(f"✅ Found '{marker}' at position {idx}")
            print(f"   Context: {text[max(0, idx-50):idx+100]}")
        else:
            print(f"❌ '{marker}' NOT found")
    
    print("\n" + "=" * 60)
    print("Full text (first 5000 chars):")
    print("=" * 60)
    print(text[:5000])
