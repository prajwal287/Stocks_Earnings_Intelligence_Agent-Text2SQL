# Shape A: unstructured filing text, chunked for keyword/semantic search
# ticker: str        -- keyword field, exact-match filterable (e.g. "AAPL")
# form_type: str      -- keyword field (e.g. "10-Q", "10-K")
# filed_date: str     -- keyword field, ISO date, filterable/sortable
# fiscal_period: str  -- keyword field (e.g. "2024-Q2")
# text: str           -- text field, tokenized + ranked (the actual MD&A chunk)
# source_url: str     -- keyword field, not searched, just carried through for citation

# Shape B: structured XBRL facts, exact lookups, not "search" at all
# ticker: str
# concept: str        -- e.g. "GrossProfit", "OperatingIncomeLoss"
# value: float
# unit: str           -- e.g. "USD"
# fiscal_period: str