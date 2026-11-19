"""Measure where CNSearchBar draws its field inside its frame (#184).

Usage: python3 issue184_measure.py SCREENSHOT.png [--expect-centred | --expect-bug]

Reads a simulator screenshot of lib/issue184_probe_entry.dart. Each bar's
frame is a magenta box (or, where the field covers it, known from the
probe's layout); the field is the run of glass pixels (neither black page nor
bright magenta frame) in a column through the empty part of the field. Prints, for each bar, how far the field's bottom
edge is from the frame's in points (negative: drawn higher). With
--expect-centred, exits 1 unless both bars are within 1 pt of their frame.
With --expect-bug, exits 1 unless the reference bar is centred and the
overlapping bar is drawn more than 1 pt higher (the bug reproduces).
"""

import sys

from PIL import Image

# iPhone 17 Pro / 16 Pro: 402 x 874 pt.
SCREEN_W_PT = 402
SCREEN_H_PT = 874
BAR_H_PT = 48
REFERENCE_TOP_PT = 300
TOLERANCE_PT = 1.0


def is_field(px):
    """The glass field: not the black page and not the bright magenta frame.

    Liquid Glass shows the magenta behind it darkened, so the field reads as
    a dim magenta; the page is black and the uncovered frame is 255,0,255.
    """
    r, g, b = px[:3]
    return r + g + b > 60 and r < 230


def field_span(img, scale, frame_top_pt):
    """Top and bottom (pt) of the white run nearest the frame's centre."""
    x = int(SCREEN_W_PT * 0.75 * scale)
    lo = max(0, int((frame_top_pt - 40) * scale))
    hi = min(img.height, int((frame_top_pt + BAR_H_PT + 10) * scale))
    rows = [y for y in range(lo, hi) if is_field(img.getpixel((x, y)))]
    if not rows:
        samples = [img.getpixel((x, y)) for y in range(lo, hi, max(1, (hi - lo) // 12))]
        print(f"  no field pixels at x={x}px; samples {samples}")
        return None
    # Group into contiguous runs and keep the longest.
    runs, start, prev = [], rows[0], rows[0]
    for y in rows[1:]:
        if y != prev + 1:
            runs.append((start, prev))
            start = y
        prev = y
    runs.append((start, prev))
    top, bottom = max(runs, key=lambda r: r[1] - r[0])
    return top / scale, (bottom + 1) / scale


def main():
    path = sys.argv[1]
    expect = "--expect-centred" in sys.argv
    expect_bug = "--expect-bug" in sys.argv
    img = Image.open(path).convert("RGB")
    scale = img.width / SCREEN_W_PT
    if abs(img.height / scale - SCREEN_H_PT) > 1:
        sys.exit(f"unexpected screen size {img.width}x{img.height}")
    bars = {
        "reference": REFERENCE_TOP_PT,
        "overlap": SCREEN_H_PT - BAR_H_PT,
    }
    ok = True
    offsets = {}
    for name, frame_top in bars.items():
        span = field_span(img, scale, frame_top)
        if span is None:
            print(f"{name}: field not found")
            ok = False
            continue
        top, bottom = span
        # The glass fades to black at its top edge, so the bottom edge is
        # the sharper measure of how far the field moved.
        offset = bottom - (frame_top + BAR_H_PT)
        print(
            f"{name}: frame {frame_top:.1f}-{frame_top + BAR_H_PT:.1f} pt, "
            f"field {top:.1f}-{bottom:.1f} pt, bottom edge {offset:+.1f} pt"
        )
        offsets[name] = offset
        if abs(offset) > TOLERANCE_PT:
            ok = False
    if expect and not ok:
        sys.exit(1)
    if expect_bug:
        ref = offsets.get("reference")
        over = offsets.get("overlap")
        if ref is None or over is None or abs(ref) > TOLERANCE_PT or over > -TOLERANCE_PT:
            sys.exit("the bug did not reproduce")
        print("bug reproduced: the overlapping bar is drawn higher")


if __name__ == "__main__":
    main()
