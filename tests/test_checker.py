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
    
@respx.mock
async def test_404_is_not_retried():
    route = respx.get("https://example.com/missing").mock(
        return_value=httpx.Response(404)
    )

    result = await check_url("https://example.com/missing")

    assert result["status"] == 404
    assert result["attempts"] == 1
    assert route.call_count == 1