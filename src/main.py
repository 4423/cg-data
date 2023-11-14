from scraping.song_scraper import SongScraper
from scraping.character_scraper import CharacterScraper
import json
from entity.song import Song
from entity.character import Character
from argparse import ArgumentParser
import urllib3
from urllib3.util.ssl_ import create_urllib3_context


def get_html(url: str) -> str:
    ctx = create_urllib3_context()
    ctx.load_default_certs()
    ctx.options |= 0x4  # ssl.OP_LEGACY_SERVER_CONNECT
    with urllib3.PoolManager(ssl_context=ctx) as http:
        r = http.request("GET", url)
        return r.data.decode("utf-8")


def get_songs() -> list[Song]:
    url = "https://dic.nicovideo.jp/a/%E3%82%A2%E3%82%A4%E3%83%89%E3%83%AB%E3%83%9E%E3%82%B9%E3%82%BF%E3%83%BC%E3%81%AE%E6%A5%BD%E6%9B%B2%E3%81%AE%E4%B8%80%E8%A6%A7"
    html = get_html(url)
    return SongScraper().get_songs(html)


def get_characters() -> list[Character]:
    url = "https://dic.nicovideo.jp/a/%E3%82%B7%E3%83%B3%E3%83%87%E3%83%AC%E3%83%A9%E3%82%AC%E3%83%BC%E3%83%AB%E3%82%BA%E5%A3%B0%E5%84%AA%E3%81%AE%E4%B8%80%E8%A6%A7"
    html = get_html(url)
    return CharacterScraper().get_characters(html)


def get(mode: str) -> list[dict]:
    if mode == "song":
        return list(map(lambda x: x.asdict(), get_songs()))
    if mode == "character":
        return list(map(lambda x: x.asdict(), get_characters()))
    return None


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--mode", type=str, choices=["song", "character"])
    args = parser.parse_args()

    d = get(args.mode)
    print(json.dumps(d, indent=2, ensure_ascii=False))
