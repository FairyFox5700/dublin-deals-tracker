from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path

from .report import render_markdown
from .tracker import collect


def main() -> int:
    parser = argparse.ArgumentParser(description="Track free and sub-€25 Dublin deals")
    parser.add_argument("--config", default="config/sources.json")
    parser.add_argument("--output", default="output")
    parser.add_argument("--max-price", type=float, default=25.0)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    offers, failures = collect(config["sources"], max_price=args.max_price)
    offers = offers[: args.limit]
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    (output / "deals.json").write_text(
        json.dumps(
            {"generated_at": generated_at, "offers": [asdict(offer) for offer in offers], "failures": failures},
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    (output / "report.md").write_text(render_markdown(offers, generated_at=generated_at), encoding="utf-8")
    print(f"Found {len(offers)} qualifying offers; {len(failures)} source failures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
