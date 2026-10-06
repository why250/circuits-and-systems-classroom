"""Acquire the Analog Mind source collection and record PDF-derived metadata.

Run with Python containing pypdf. PDFs, extracted text, and page previews stay
under the gitignored reference/ directory; the source manifest is versioned.
This command acquires sources; it does not mark them as read or verified notes.
"""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import urllib.request
from urllib.parse import urljoin

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "reference" / "razavi"
MANIFEST = ROOT / "sources" / "razavi-analog-mind.json"
SOURCE_URL = "https://www.seas.ucla.edu/brweb/journal.html"
# These two PDFs identify the column on their first pages despite missing HTML labels.
UNLABELED_MEMBERS = {"BR_SSCM_Fall_2022.pdf", "BR_SSCM_2_2022.pdf"}


class JournalLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.href = None
        self.label = []
        self.items = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.href = dict(attrs).get("href")
            self.label = []

    def handle_data(self, data):
        if self.href is not None:
            self.label.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self.href is not None:
            label = " ".join(" ".join(self.label).split())
            url = urljoin(SOURCE_URL, self.href)
            if "analog mind" in label.lower() or url.rsplit("/", 1)[-1] in UNLABELED_MEMBERS:
                self.items.append({"url": url, "website_citation": label})
            self.href = None


def acquire(item):
    name = item["url"].rsplit("/", 1)[-1]
    path = REFERENCE / name
    if not path.exists():
        data = urllib.request.urlopen(item["url"], timeout=45).read()
        if not data.startswith(b"%PDF"):
            raise ValueError(f"Not a PDF: {item['url']}")
        temporary = path.with_suffix(".pdf.part")
        temporary.write_bytes(data)
        temporary.replace(path)
    reader = PdfReader(path)
    pages = [page.extract_text() or "" for page in reader.pages]
    first = " ".join(pages[0].split()).replace("S UMMER", "SUMMER")
    if "THE ANALOG MIND" not in first.upper():
        raise ValueError(f"PDF does not identify the expected column: {name}")
    doi_match = re.search(r"10\.1109/\s*MSSC\.\d{4}\.\d+", first)
    season_match = re.search(r"\b(WINTER|SPRING|SUMMER|FALL)\s+(20\d{2})\b", first, re.I)
    title_match = re.search(r'"(.*?)"', item["website_citation"])
    title = title_match.group(1).replace(" [The Analog Mind]", "").rstrip(",") if title_match else name
    printed_pages = []
    for text in pages:
        header = " ".join(text[:250].split())
        for season in ("WINTER", "SPRING", "SUMMER", "FALL"):
            header = re.sub(r"\b" + r"\s*".join(season) + r"\b", season, header, flags=re.I)
        match = re.search(r"\b(?:WINTER|SPRING|SUMMER|FALL)\s+20\d{2}\s+(\d+)\b", header, re.I)
        if not match:
            match = re.match(r"\s*(\d+)\s+(?:WINTER|SPRING|SUMMER|FALL)\b", header, re.I)
        printed_pages.append(int(match.group(1)) if match else None)
    text_path = REFERENCE / (path.stem + ".txt")
    text_path.write_text("\n\n".join(f"=== PDF PAGE {i + 1} ===\n{text}" for i, text in enumerate(pages)), encoding="utf-8")
    return {
        **item,
        "title": title,
        "pdf_filename": name,
        "pdf_pages": len(pages),
        "printed_pages": printed_pages,
        "doi": re.sub(r"\s", "", doi_match.group(0)) if doi_match else None,
        "season": season_match.group(1).title() if season_match else None,
        "year": int(season_match.group(2)) if season_match else None,
        "sha256": sha256(path.read_bytes()).hexdigest(),
        "column_verified_from_pdf": True,
        "full_text_read": False,
        "original_pages_reviewed": False,
        "reviewed_at": None,
        "marker_conversion": "pending",
        "note": None,
        "note_status": "pending",
    }


def main():
    REFERENCE.mkdir(parents=True, exist_ok=True)
    html = urllib.request.urlopen(SOURCE_URL, timeout=30).read()
    (REFERENCE / "journal.html").write_bytes(html)
    parser = JournalLinks()
    parser.feed(html.decode("utf-8", errors="replace"))
    unique = {item["url"]: item for item in parser.items}
    previous = {}
    if MANIFEST.exists():
        previous = {item["url"]: item for item in json.loads(MANIFEST.read_text(encoding="utf-8"))["articles"]}
    with ThreadPoolExecutor(max_workers=3) as pool:
        articles = list(pool.map(acquire, unique.values()))
    for item in articles:
        old = previous.get(item["url"], {})
        if old.get("sha256") == item["sha256"]:
            for field in ("full_text_read", "original_pages_reviewed", "reviewed_at",
                          "marker_conversion", "note", "note_status", "verification_record"):
                if field in old:
                    item[field] = old[field]
        print(f"{item['year']} {item['season']}: {item['title']} | {item['pdf_pages']} PDF pages | {item['doi']}")
    payload = {
        "source_url": SOURCE_URL,
        "acquired_at": datetime.now(timezone.utc).isoformat(),
        "scope": "Analog Mind, including PDF-confirmed unlabeled HTML entries; other columns excluded",
        "articles": articles,
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Acquired {len(articles)} PDFs. Manifest: {MANIFEST}")


if __name__ == "__main__":
    main()
