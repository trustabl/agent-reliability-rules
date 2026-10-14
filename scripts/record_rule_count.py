"""Record one dated point of the pack's rule count.

    python3 scripts/record_rule_count.py <count>

The badge carries only the current number, so it answers "how many rules are
there" but never "how fast is the pack growing". This keeps the series.

One point per day, upserted, so several pushes in a day collapse to that day's
final count rather than nine entries. The count is passed in rather than
recomputed here: it comes from `trustabl rules validate`, which the validate
workflow has already run, and deriving it a second way would let the two
disagree.
"""

import datetime
import json
import pathlib
import sys

HISTORY = pathlib.Path(".github/stats/rule-count-history.json")

EMPTY = {
    "repo": "trustabl/agent-reliability-rules",
    "unit": "rules_in_pack",
    "source": "trustabl rules validate",
    "history": [],
}


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: record_rule_count.py <count>")
    raw = sys.argv[1].strip()
    if not raw.isdigit():
        # An empty or unparsed count means the validator's output changed shape.
        # Fail loudly: a silently skipped point leaves a flat line that reads as
        # "no rules were added" rather than "nothing was recorded".
        sys.exit(f"rule count {raw!r} is not a number; the validator output may have changed")
    count = int(raw)

    doc = json.loads(HISTORY.read_text(encoding="utf-8")) if HISTORY.exists() else dict(EMPTY)

    day = datetime.date.today().isoformat()  # UTC on the runner
    points = {p["date"]: p for p in doc.get("history", [])}
    points[day] = {"date": day, "rules": count}
    doc["history"] = [points[d] for d in sorted(points)]

    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    HISTORY.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(f"{day}: {count} rules ({len(doc['history'])} points)")


if __name__ == "__main__":
    main()
