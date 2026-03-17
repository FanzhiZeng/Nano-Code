from html.parser import HTMLParser
from urllib.parse import parse_qs, quote_plus, urlparse
from urllib.request import Request, urlopen

from .base import Tool


MAX_RESULTS = 5
SEARCH_URL = "https://html.duckduckgo.com/html/?q="


class DuckDuckGoHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.results: list[dict[str, str]] = []
        self._in_result_link = False
        self._current_href = ""
        self._current_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return

        attr_map = dict(attrs)
        classes = attr_map.get("class", "") or ""
        if "result__a" not in classes:
            return

        self._in_result_link = True
        self._current_href = attr_map.get("href", "") or ""
        self._current_text = []

    def handle_data(self, data: str) -> None:
        if self._in_result_link:
            self._current_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or not self._in_result_link:
            return

        title = "".join(self._current_text).strip()
        if title and self._current_href:
            self.results.append(
                {
                    "title": title,
                    "url": extract_result_url(self._current_href),
                }
            )

        self._in_result_link = False
        self._current_href = ""
        self._current_text = []


def extract_result_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.netloc.endswith("duckduckgo.com") and parsed.path == "/l/":
        query = parse_qs(parsed.query)
        return query.get("uddg", [url])[0]
    return url


def web_search(query: str, max_results: int = MAX_RESULTS) -> str:
    request = Request(
        SEARCH_URL + quote_plus(query),
        headers={"User-Agent": "nano-code/0.1"},
    )

    with urlopen(request, timeout=15) as response:
        html = response.read().decode("utf-8", errors="replace")

    parser = DuckDuckGoHTMLParser()
    parser.feed(html)

    results = parser.results[:max_results]
    if not results:
        return f"No results found for: {query}"

    lines = []
    for index, result in enumerate(results, start=1):
        lines.append(f"{index}. {result['title']}")
        lines.append(f"   {result['url']}")
    return "\n".join(lines)


def web_search_handler(tool_input: dict[str, str | int]) -> str:
    query = str(tool_input["query"])
    max_results = int(tool_input.get("max_results", MAX_RESULTS))
    max_results = max(1, min(max_results, MAX_RESULTS))
    return web_search(query, max_results=max_results)


WEB_SEARCH_TOOL = Tool(
    name="web_search",
    description="Search the web and return a short list of results.",
    input_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "max_results": {"type": "integer"},
        },
        "required": ["query"],
    },
    handler=web_search_handler,
)
