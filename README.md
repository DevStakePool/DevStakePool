# DEV - Cardano Stake Pool

## A Cardano stake pool repository that helps and supports people in underdeveloped countries to complete their education carreer 

---

## `split_donations.py` — Donation screenshot splitter

Splits a Western Union screenshot (containing multiple donation cards) into individual JPEG files, named after the existing donations convention.

**Requirements:** ImageMagick (`brew install imagemagick`)

**Usage:**

```bash
python3 split_donations.py <screenshot.png> <output_dir> \
    "Name - Country=YYYY-MM-DD" \
    "Name - Country=YYYY-MM-DD" \
    ...
```

Entries are listed **top-to-bottom** as they appear in the screenshot. The script auto-detects card boundaries; if detection fails it falls back to equal division.

**Example:**

```bash
python3 split_donations.py ~/Downloads/screenshot.png donations/ \
    "Aliou - Senegal=2026-04-03" \
    "Aliou - Senegal=2026-03-18" \
    "Aliou - Senegal=2026-03-02" \
    "Aliou - Senegal=2026-01-31" \
    "Aliou - Senegal=2026-01-01" \
    "Aliou - Senegal=2025-12-21" \
    "Aliou - Senegal=2025-12-01"
```

Output files follow the naming convention already used in `donations/`: `Name - Country - YYYY-MM-DD.jpg`

