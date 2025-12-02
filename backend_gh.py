import os
import json
import requests
import xml.etree.ElementTree as ET
from pathlib import Path

# URL RSS fournie par FreshRSS, passée via un secret GitHub
RSS_URL = os.environ["FRESHRSS_RSS_URL"]

OUT_DIR = Path("public")
OUT_DIR.mkdir(exist_ok=True)
OUT_FILE = OUT_DIR / "anynews.json"


def fetch_and_parse_rss():
    print(f"[AnyNews] Fetch RSS: {RSS_URL}")
    r = requests.get(RSS_URL, timeout=15)
    r.raise_for_status()
    xml = r.text

    root = ET.fromstring(xml)
    channel = root.find("channel")
    if channel is None:
        print("[AnyNews] Pas de <channel> dans le RSS")
        return []

    articles = []
    for item in channel.findall("item"):
        title = item.findtext("title", default="(Sans titre)")
        link = item.findtext("link", default="")
        pubdate = item.findtext("pubDate", default="")
        desc = item.findtext("description", default="")

        # contenu complet parfois dans <content:encoded>
        content_encoded = item.find(
            "{http://purl.org/rss/1.0/modules/content/}encoded"
        )
        if content_encoded is not None and content_encoded.text:
            desc = content_encoded.text

        articles.append({
            "id": link,
            "title": title,
            "feed": "FreshRSS",
            "date": pubdate,
            "content": desc,
        })

    return articles


def main():
    articles = fetch_and_parse_rss()
    print(f"[AnyNews] Articles: {len(articles)}")
    OUT_FILE.write_text(json.dumps(articles, indent=2), encoding="utf-8")
    print(f"[AnyNews] Écrit dans {OUT_FILE}")


if __name__ == "__main__":
    main()
