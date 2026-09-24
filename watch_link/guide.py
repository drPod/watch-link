import argparse
import gzip
import os
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.request import urlopen

from defusedxml.ElementTree import iterparse


def refresh(url: str, channels: set[str], output: Path) -> tuple[int, int]:
    if not url.startswith("https://") or not channels:
        raise ValueError("An HTTPS guide and at least one channel ID are required")
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=output.parent, suffix=".xml")
    temporary = Path(name)
    counts = [0, 0]
    try:
        with os.fdopen(fd, "wb") as target, urlopen(url, timeout=60) as response:
            source = gzip.GzipFile(fileobj=response) if url.endswith(".gz") else response
            parser = iterparse(source, events=("start", "end"))
            _, root = next(parser)
            if root.tag != "tv":
                raise ValueError("Guide is not an XMLTV document")
            target.write(b'<?xml version="1.0" encoding="utf-8"?>\n<tv>\n')
            for event, element in parser:
                if event != "end" or element.tag not in ("channel", "programme"):
                    continue
                key = "id" if element.tag == "channel" else "channel"
                if element.get(key) in channels:
                    target.write(ET.tostring(element, encoding="utf-8"))
                    counts[element.tag == "programme"] += 1
                root.remove(element)
            target.write(b"</tv>\n")
        if not all(counts):
            raise ValueError("Guide has no matching channels or programmes; previous guide preserved")
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
    return counts[0], counts[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Stream-filter an XMLTV feed without loading the full guide")
    parser.add_argument("--url", required=True)
    parser.add_argument("--channels", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    channels = {line.strip() for line in args.channels.read_text().splitlines() if line.strip()}
    print("Guide channels/programmes:", refresh(args.url, channels, args.output))


if __name__ == "__main__":
    main()
