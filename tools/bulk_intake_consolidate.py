
# python tools/bulk_intake_consolidate.py

#!/usr/bin/env python3
"""
tools/bulk_intake_consolidate.py

Reads Main/data/GET--intakes/intakes.json and extracts all unique
(vintage, block_name) pairs from the "composition" entries. By default the
script only outputs pairs with vintage >= 2023.

Writes the result as JSON to an output file (default:
Main/data/GET--intakes/vintage_block_pairs.json) and prints a small summary.

Usage:
    python tools/bulk_intake_consolidate.py \
        --input Main/data/GET--intakes/intakes.json \
        --output Main/data/GET--intakes/vintage_block_pairs.json \
        --min-vintage 2023
"""

import argparse
import json
import re
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple


def try_load_json(content: str) -> List[Dict[str, Any]]:
    """Try multiple strategies to parse JSON content into a list of objects."""
    content = content.strip()
    if not content:
        return []

    # Strategy 1: normal JSON (array or single object)
    try:
        obj = json.loads(content)
        if isinstance(obj, list):
            return obj
        if isinstance(obj, dict):
            return [obj]
    except json.JSONDecodeError:
        pass

    # Strategy 2: JSON Lines (one JSON object per line)
    lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
    objs = []
    parsed_all_lines = True
    for ln in lines:
        try:
            parsed = json.loads(ln)
            objs.append(parsed)
        except json.JSONDecodeError:
            parsed_all_lines = False
            break
    if parsed_all_lines and objs:
        return objs

    # Strategy 3: attempt to repair concatenated objects by inserting commas between "}{"
    repaired = re.sub(r"}\s*{", "},{", content)
    repaired = f"[{repaired}]"  # wrap as array
    try:
        obj = json.loads(repaired)
        if isinstance(obj, list):
            return obj
    except json.JSONDecodeError:
        pass

    # If none worked, raise error
    raise ValueError("Failed to parse JSON content with known strategies.")


def extract_pairs(
    intakes: Iterable[Dict[str, Any]],
    min_vintage: Optional[int] = 2023,
    include_nulls: bool = False
) -> List[Dict[str, Any]]:
    """
    Extract unique (vintage, block_name) pairs from intake objects.

    - min_vintage: if set, only include pairs where vintage >= min_vintage.
                   If None, do not filter by vintage.
    - include_nulls: if True, include pairs where vintage or block_name is missing/null.
    """
    seen: Set[Tuple[Optional[int], Optional[str]]] = set()

    for intake in intakes:
        composition = intake.get("composition") or []
        if not isinstance(composition, list):
            # Some unexpected shapes: skip
            continue
        for comp in composition:
            vintage = comp.get("vintage")
            block = comp.get("block")
            block_name: Optional[str] = None
            if isinstance(block, dict):
                block_name = block.get("name")
            elif isinstance(block, str):
                block_name = block

            # normalize vintage type
            if isinstance(vintage, (int, float)):
                try:
                    vintage = int(vintage)
                except Exception:
                    pass

            # filter out nulls unless include_nulls is True
            if vintage is None or block_name is None:
                if not include_nulls:
                    continue

            # enforce min_vintage if provided (skip missing vintages)
            if min_vintage is not None:
                if vintage is None:
                    continue
                try:
                    if int(vintage) < int(min_vintage):
                        continue
                except Exception:
                    # if vintage can't be compared, skip it
                    continue

            if block_name is not None:
                block_name = str(block_name)

            seen.add((vintage, block_name))

    # Sort deterministically: by vintage descending (None last) then block_name ascending (None last)
    def sort_key(t: Tuple[Optional[int], Optional[str]]):
        vintage, block_name = t
        # vintage: higher vintages first; None -> -inf -> placed last via large positive
        vintage_key = -vintage if isinstance(vintage, int) else float("inf")
        # block_name: alphabetical, None last
        block_key = ("" if block_name is None else block_name)
        none_flag = 1 if block_name is None else 0
        return (vintage_key, none_flag, block_key)

    sorted_pairs = sorted(list(seen), key=sort_key)

    return [{"vintage": v, "block_name": b} for (v, b) in sorted_pairs]


def main():
    p = argparse.ArgumentParser(description="Collect unique vintage & block_name pairs")
    p.add_argument(
        "--input", "-i",
        default="Main/data/GET--intakes/intakes.json",
        help="Path to intakes.json"
    )
    p.add_argument(
        "--output", "-o",
        default="Main/data/GET--intakes/vintage_block_pairs.json",
        help="Output JSON file"
    )
    p.add_argument(
        "--min-vintage",
        type=int,
        default=2023,
        help="Minimum vintage (inclusive). Use 0 to disable filtering (no min). Default: 2023"
    )
    p.add_argument(
        "--include-nulls",
        action="store_true",
        help="Include pairs where vintage or block_name is missing/null"
    )
    args = p.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as fh:
            content = fh.read()
    except FileNotFoundError:
        print(f"Error: input file not found: {args.input}")
        raise SystemExit(1)

    try:
        intakes = try_load_json(content)
    except ValueError as e:
        print("Failed to parse input JSON:", str(e))
        raise SystemExit(1)

    min_vintage_val = None if args.min_vintage == 0 else args.min_vintage
    pairs = extract_pairs(intakes, min_vintage=min_vintage_val, include_nulls=args.include_nulls)

    with open(args.output, "w", encoding="utf-8") as outfh:
        json.dump(pairs, outfh, indent=2, ensure_ascii=False)

    if min_vintage_val is None:
        print(f"Wrote {len(pairs)} unique (vintage, block_name) pairs to {args.output} (no min vintage filter)")
    else:
        print(f"Wrote {len(pairs)} unique (vintage >= {min_vintage_val}, block_name) pairs to {args.output}")


if __name__ == "__main__":
    main()