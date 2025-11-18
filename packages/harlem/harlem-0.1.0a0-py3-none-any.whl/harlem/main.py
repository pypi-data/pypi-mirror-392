import asyncio
import threading
import time
import warnings
from contextlib import suppress
from typing import Set

from harlem.exporters.base import HarExporter
from harlem.models.har import Page, Entry
from harlem.record import record_to_file
from harlem.recorders import RequestsHarRecorder


def get_google():
    import requests

    url = "https://8.8.8.8/"

    payload = {}
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "he,en;q=0.9,he-IL;q=0.8,en-US;q=0.7",
        "sec-ch-ua": '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "sec-ch-ua-arch": '"x86"',
        "sec-ch-ua-bitness": '"64"',
        "sec-ch-ua-full-version-list": '"Google Chrome";v="123.0.6312.60", "Not:A-Brand";v="8.0.0.0", "Chromium";v="123.0.6312.60"',
        "sec-ch-ua-model": '""',
        "sec-ch-ua-platform-version": '"10.0.0"',
        "sec-ch-ua-wow64": "?0",
        "cache-control": "max-age=0",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Referer": "",
        "Origin": "https://dns.google",
        "referer": "https://dns.google/",
    }

    response = requests.get(
        "https://link.testfile.org/60M",
        headers=headers,
        data={},
        cookies={"foo": "bar"},
        allow_redirects=False,
    )
    print(response.status_code)

    response = requests.get("https://8.8.8.8/", headers=headers, data={})
    print(response.status_code)

    response = requests.post(
        "http://example.com/", headers=headers, data={"payload": "test"}
    )
    print(response.status_code)


async def async_get_google():
    import aiohttp

    payload = {}
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "he,en;q=0.9,he-IL;q=0.8,en-US;q=0.7",
        "sec-ch-ua": '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "sec-ch-ua-arch": '"x86"',
        "sec-ch-ua-bitness": '"64"',
        "sec-ch-ua-full-version-list": '"Google Chrome";v="123.0.6312.60", "Not:A-Brand";v="8.0.0.0", "Chromium";v="123.0.6312.60"',
        "sec-ch-ua-model": '""',
        "sec-ch-ua-platform-version": '"10.0.0"',
        "sec-ch-ua-wow64": "?0",
        "cache-control": "max-age=0",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Referer": "",
        "Origin": "https://dns.google",
        "referer": "https://dns.google/",
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://link.testfile.org/60M",
            headers=headers,
            data={},
            cookies={"foo": "bar"},
            allow_redirects=False,
        ) as response:
            print(response.status)

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://8.8.8.8/", headers=headers, data={}
        ) as response:
            print(response.status)

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://example.com/", headers=headers, data={"payload": "test"}
        ) as response:
            print(response.status)


def nested_test2():
    get_google()


def debug_obj(obj: object, prefix: str = "", cached_ids: Set[int] = None) -> dict:
    if cached_ids is None:
        cached_ids = set()

    all_attrs = {}
    if id(obj) in cached_ids:
        return all_attrs
    cached_ids.add(id(obj))
    all_attrs[prefix] = (str(type(obj)), str(obj))

    for attr in dir(obj):
        if attr.startswith("__"):
            continue
        value = getattr(obj, attr)
        if value is obj:
            continue
        if isinstance(value, (str, int, float, bool, type(None))):
            all_attrs[f"{prefix}.{attr}"] = (str(type(value)), str(value))
        elif isinstance(value, dict):
            for k, v in value.items():
                all_attrs.update(debug_obj(v, f"{prefix}.{attr}[{k}]", cached_ids))
        elif isinstance(value, list):
            for i, v in enumerate(value):
                all_attrs.update(debug_obj(v, f"{prefix}.{attr}[{i}]", cached_ids))
        else:
            all_attrs.update(debug_obj(value, f"{prefix}.{attr}", cached_ids))

    return all_attrs


def reddit_api():
    import datetime

    import praw

    r = praw.Reddit(
        client_id="8cUEH7PO2u1ddA",
        client_secret="MmG7oH8mrFgtwTx6F5iH7AXKdWQ",
        user_agent="boomboom",
    )

    subreddit = r.subreddit("anarchychess")
    for submission in r.front.hot(limit=1000):
        time.sleep(0.05)
        print(
            f"[{datetime.datetime.fromtimestamp(submission.created)}] {submission.title} - Score: {submission.score}"
        )


async def async_reddit_api():
    import datetime

    import asyncpraw

    r = asyncpraw.Reddit(
        client_id="8cUEH7PO2u1ddA",
        client_secret="MmG7oH8mrFgtwTx6F5iH7AXKdWQ",
        user_agent="boomboom",
    )

    # subreddit = r.subreddit('anarchychess')
    async for submission in r.front.hot(limit=256):
        time.sleep(0.05)
        print(
            f"[{datetime.datetime.fromtimestamp(submission.created)}] {submission.title} - Score: {submission.score}"
        )

    await r.close()


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    def nested_test1():
        nested_test2()

    async def async_main():
        await async_get_google()
        await async_reddit_api()

    with record_to_file(
        "../assets/final.har",
        indent=4,
        live=True,
        interval_seconds=1,
    ) as har:
        asyncio.run(async_main())
        get_google()
        # nested_test1()
        # reddit_api()
        # nested_test1()

    # with open("output3.har", "w", encoding="utf-8") as f:
    #     exporter.save(f)
    # exporter.save("output4.har")
    # exporter.save(Path("output5.har"))
