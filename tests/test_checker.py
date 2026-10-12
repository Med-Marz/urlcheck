import httpx
import pytest
import respx

from urlcheck.checker import check_url, check_urls
from urlcheck.cli import read_urls, split_valid_urls


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    async def fake_sleep(seconds):
        pass

    monkeypatch.setattr("urlcheck.checker.asyncio.sleep", fake_sleep)


@respx.mock
async def test_working_site_returns_200():
    respx.get("https://example.com").mock(return_value=httpx.Response(200))

    result = await check_url("https://example.com")

    assert result["url"] == "https://example.com"
    assert result["status"] == 200
    assert result["error"] is None
    assert result["attempts"] == 1


@respx.mock
async def test_404_is_not_retried():
    route = respx.get("https://example.com/missing").mock(
        return_value=httpx.Response(404)
    )

    result = await check_url("https://example.com/missing")

    assert result["status"] == 404
    assert result["attempts"] == 1
    assert route.call_count == 1


@respx.mock
async def test_server_error_then_success():
    route = respx.get("https://example.com").mock(
        side_effect=[httpx.Response(500), httpx.Response(200)]
    )

    result = await check_url("https://example.com")

    assert result["status"] == 200
    assert result["attempts"] == 2
    assert route.call_count == 2


@respx.mock
async def test_gives_up_after_three_attempts():
    route = respx.get("https://example.com").mock(
        return_value=httpx.Response(500)
    )

    result = await check_url("https://example.com")

    assert result["status"] == 500
    assert result["attempts"] == 3
    assert route.call_count == 3


@respx.mock
async def test_timeout_is_reported():
    route = respx.get("https://example.com").mock(
        side_effect=httpx.ConnectTimeout("too slow")
    )

    result = await check_url("https://example.com")

    assert result["status"] is None
    assert result["error"] == "timeout"
    assert result["attempts"] == 3
    assert route.call_count == 3


@respx.mock
async def test_check_urls_returns_all_results_in_order():
    respx.get("https://a.example").mock(return_value=httpx.Response(200))
    respx.get("https://b.example").mock(return_value=httpx.Response(404))
    respx.get("https://c.example").mock(return_value=httpx.Response(200))

    results = await check_urls(
        ["https://a.example", "https://b.example", "https://c.example"],
        max_concurrent=2,
    )

    assert [r["status"] for r in results] == [200, 404, 200]


def test_read_urls_skips_blank_lines_and_comments(tmp_path):
    file = tmp_path / "urls.txt"
    file.write_text("https://a.example\n\n# a comment\n  https://b.example  \n")

    assert read_urls(file) == ["https://a.example", "https://b.example"]


def test_split_valid_urls_separates_bad_entries():
    valid, invalid = split_valid_urls(
        ["https://a.example", "github.com", "ftp://b.example", "http://", "not a url"]
    )

    assert valid == ["https://a.example"]
    assert invalid == ["github.com", "ftp://b.example", "http://", "not a url"]