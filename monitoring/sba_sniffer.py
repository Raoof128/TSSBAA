"""In-lab SBA sniffer that replays captured HTTP exchanges for analysis."""
from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()


class SBASniffer:
    """Reads JSONL capture files and renders suspicious events."""

    def __init__(self, capture_path: Path) -> None:
        self.capture_path = capture_path

    def load_events(self) -> Iterable[dict[str, str]]:
        with self.capture_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                yield json.loads(line)

    def render_alerts(self, events: Iterable[dict[str, str]]) -> None:
        table = Table(title="SBA Security Alerts")
        table.add_column("timestamp")
        table.add_column("source")
        table.add_column("path")
        table.add_column("verdict")
        table.add_column("details")

        for event in events:
            verdict = event.get("verdict", "unknown")
            style = "green" if verdict == "allowed" else "red"
            table.add_row(
                event.get("ts", "n/a"),
                event.get("source", "unknown"),
                event.get("path", "n/a"),
                verdict,
                event.get("details", ""),
                style=style,
            )

        console.print(table)


def demo_render(capture_file: str) -> None:  # pragma: no cover - demo
    sniffer = SBASniffer(Path(capture_file))
    sniffer.render_alerts(sniffer.load_events())


if __name__ == "__main__":  # pragma: no cover - manual execution helper
    demo_render("./docs/sample_captures/sba_events.jsonl")
