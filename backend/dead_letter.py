"""
File-based dead-letter queue for car-sniper.
Captures failed ad payloads so they can be replayed / inspected later.

Usage:
    from backend.dead_letter import dead_letter
    dead_letter.save(ad_payload, error="timeout", source="olx_scraper")
"""

import json
import os
import time
from datetime import datetime, timezone
from typing import Optional


DEAD_LETTER_DIR = os.path.join(os.path.dirname(__file__), "..", "dead_letter")


class DeadLetterQueue:
    """Append-only JSON-lines dead-letter store on the filesystem."""

    def __init__(self, directory: str = DEAD_LETTER_DIR):
        self.directory = os.path.abspath(directory)

    def _ensure_dir(self) -> None:
        os.makedirs(self.directory, exist_ok=True)

    def _write_path(self, source: str) -> str:
        """Rotates daily: dead_letter/olx_scraper_2026-06-29.jsonl"""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        safe_source = source.replace("/", "_").replace(" ", "_")
        return os.path.join(self.directory, f"{safe_source}_{today}.jsonl")

    def save(
        self,
        payload: dict,
        error: str = "",
        source: str = "unknown",
        context: Optional[dict] = None,
    ) -> None:
        """Persist a failed ad payload as a JSON line."""
        self._ensure_dir()
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "source": source,
            "error": str(error),
            "payload": payload,
            "context": context or {},
        }
        path = self._write_path(source)
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
        except Exception:
            # Last-resort: don't crash the scraper because of DLQ file I/O
            import sys
            print(
                f"dead_letter: failed to write to {path}",
                file=sys.stderr,
            )

    def replay_iter(self, source: str = "", date_str: str = ""):
        """Generator that yields (record_dict) from a dead-letter file.

        Args:
            source: e.g. 'olx_scraper'. If empty, reads all sources.
            date_str: 'YYYY-MM-DD'. If empty, defaults to today.
        """
        from glob import glob
        date_str = date_str or datetime.now(timezone.utc).strftime("%Y-%m-%d")
        pattern = f"{source}_*{date_str}.jsonl" if source else f"*_{date_str}.jsonl"
        for path in sorted(glob(os.path.join(self.directory, pattern))):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            yield json.loads(line)
                        except json.JSONDecodeError:
                            continue


# Global singleton
dead_letter = DeadLetterQueue()
