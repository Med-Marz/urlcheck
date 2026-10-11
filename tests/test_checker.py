import httpx
import pytest
import respx

from urlcheck.checker import check_url


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