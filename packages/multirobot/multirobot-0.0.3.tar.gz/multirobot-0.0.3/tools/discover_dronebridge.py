#!/usr/bin/env python3
import asyncio
import sys
from aiohttp import ClientSession, ClientError
from html.parser import HTMLParser

class TitleParser(HTMLParser):
    """Grab the content of the <title> tag."""
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.chunks = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'title':
            self.in_title = True

    def handle_data(self, data):
        if self.in_title:
            self.chunks.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == 'title':
            self.in_title = False

    @property
    def title(self):
        return ''.join(self.chunks).strip()

async def fetch_title(session: ClientSession, ip: str, timeout: int = 5):
    url = f'http://{ip}/'
    try:
        async with session.get(url, timeout=timeout) as resp:
            text = await resp.text(errors='ignore')
    except asyncio.TimeoutError:
        return ip, '', 'timeout'
    except ClientError as e:
        return ip, '', f'HTTP error: {e}'
    except Exception as e:
        return ip, '', str(e)

    parser = TitleParser()
    parser.feed(text)
    title = parser.title
    return ip, title, ''

async def main():
    # 1) Create one session with a common UA header
    headers = {'User-Agent': 'Mozilla/5.0'}
    async with ClientSession(headers=headers) as session:
        # 2) Launch all 30 coroutines at once
        tasks = [
            fetch_title(session, f'192.168.1.{i}')
            for i in range(1, 31)
        ]
        results = await asyncio.gather(*tasks)

    # 3) Print out findings
    for ip, title, err in results:
        if err == '':
            print(f'{ip} → ✅: "{title}"')
        else:
            print(f'{ip} → ❌ error: {err}')

if __name__ == '__main__':
    asyncio.run(main())

