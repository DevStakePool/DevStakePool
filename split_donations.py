#!/usr/bin/env python3
"""
Split a donation screenshot into individual JPEG files.

Usage:
    python3 split_donations.py <screenshot.png> <output_dir> \
        "Name - Country=YYYY-MM-DD" ...

Entries are listed top-to-bottom as they appear in the screenshot.

Example:
    python3 split_donations.py screenshot.png donations/ \
        "Aliou - Senegal=2026-04-03" \
        "Aliou - Senegal=2026-03-18"
"""

import subprocess
import sys
from pathlib import Path


def get_image_size(image_path):
    result = subprocess.run(
        ['magick', 'identify', '-format', '%wx%h', str(image_path)],
        capture_output=True, text=True, check=True,
    )
    w, h = result.stdout.strip().split('x')
    return int(w), int(h)


def detect_boundaries_smart(image_path, num_cards):
    """Detect card boundaries by finding bright rows (gaps between cards)."""
    # Scale to 1px wide to get per-row average color
    result = subprocess.run(
        ['magick', str(image_path), '-resize', '1x!', '-depth', '8', 'txt:-'],
        capture_output=True, text=True, check=True,
    )

    # Parse pixel values — format: "X,Y: (R,G,B)  #RRGGBB  ..."
    row_brightness = []
    for line in result.stdout.splitlines():
        if ':' not in line or line.startswith('#'):
            continue
        try:
            inner = line.split('(')[1].split(')')[0].split(',')
            r, g, b = int(inner[0]), int(inner[1]), int(inner[2])
            row_brightness.append((r + g + b) / 3)
        except (IndexError, ValueError):
            continue

    if not row_brightness:
        return None

    max_brightness = max(row_brightness)
    threshold = max_brightness * 0.98

    # Find transitions between content and gap rows
    is_gap = [b >= threshold for b in row_brightness]
    card_starts = [0]
    card_ends = []
    in_gap = False
    gap_start = 0

    for i in range(1, len(is_gap)):
        if not in_gap and is_gap[i]:
            in_gap = True
            gap_start = i
        elif in_gap and not is_gap[i]:
            in_gap = False
            cut = (gap_start + i) // 2
            card_ends.append(cut)
            card_starts.append(cut)

    card_ends.append(len(row_brightness))

    if len(card_starts) != num_cards:
        return None

    return list(zip(card_starts, card_ends))


def detect_boundaries_equal(image_path, num_cards):
    """Fall back to equal division."""
    _, h = get_image_size(image_path)
    card_h = h / num_cards
    return [(round(i * card_h), round((i + 1) * card_h)) for i in range(num_cards)]


def detect_boundaries(image_path, num_cards):
    boundaries = detect_boundaries_smart(image_path, num_cards)
    if boundaries:
        print(f"Smart detection: found {num_cards} card boundaries.")
    else:
        print("Smart detection failed — falling back to equal division.")
        boundaries = detect_boundaries_equal(image_path, num_cards)
    return boundaries


def split_donations(image_path, output_dir, entries, quality=90):
    image_path = Path(image_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    width, _ = get_image_size(image_path)
    boundaries = detect_boundaries(image_path, len(entries))

    for (name_prefix, date_str), (y_start, y_end) in zip(entries, boundaries):
        height = y_end - y_start
        filename = f"{name_prefix} - {date_str}.jpg"
        output_path = output_dir / filename

        subprocess.run(
            [
                'magick', str(image_path),
                '-crop', f'{width}x{height}+0+{y_start}',
                '+repage',
                '-quality', str(quality),
                str(output_path),
            ],
            check=True,
        )
        print(f"  Created: {filename}")


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    image_path = sys.argv[1]
    output_dir = sys.argv[2]
    raw_entries = sys.argv[3:]

    entries = []
    for raw in raw_entries:
        if '=' not in raw:
            print(f"Error: entry '{raw}' missing '=' separator. Expected 'Name - Country=YYYY-MM-DD'")
            sys.exit(1)
        name_prefix, date_str = raw.rsplit('=', 1)
        entries.append((name_prefix.strip(), date_str.strip()))

    print(f"Processing {len(entries)} cards from {image_path}")
    split_donations(image_path, output_dir, entries)
    print("Done.")


if __name__ == '__main__':
    main()
