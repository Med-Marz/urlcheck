import httpx
import respx

from urlcheck.checker import check_url


@respx.mock
async def test_working_site_returns_200():
    respx.get("https://example.com").mock(return_value=httpx.Response(200))

    result = await check_url("https://example.com")

    assert result["url"] == "https://example.com"
    assert result["status"] == 200
    assert result["error"] is None
    assert result["attempts"] == 1