from urllib.parse import quote_plus, urlencode
from datasette.app import Datasette
import pytest


@pytest.mark.asyncio
async def test_plugin_is_installed():
    datasette = Datasette(memory=True)
    response = await datasette.client.get("/-/plugins.json")
    assert response.status_code == 200
    installed_plugins = {p["name"] for p in response.json()}
    assert "datasette-proxy-image-tags" in installed_plugins


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value,expect_img",
    (
        (1, False),
        (1.2, False),
        (None, False),
        ("https://blah/has_url.png", True),
        ("http://blah/has_url.jpg", True),
        ("https://blah/has_url.jpeg", True),
        ("https://blah/has_url.gif", True),
        (" https://blah/has_url.gif ", True),
    ),
)
async def test_image(value, expect_img):
    datasette = Datasette(memory=True, metadata={
        "plugins": {
            "datasette-proxy-image-tags": {
                "columns": ["value"],
            }
        }
    })
    response = await datasette.client.get(
        "/_memory?"
        + urlencode(
            {
                "sql": "select :value as value",
                "value": value,
            }
        )
    )
    assert response.status_code == 200
    html = response.text
    if expect_img:
        expected = '<img src="/-/proxy?url={}" width="200" loading="lazy">'.format(
            quote_plus(value.strip())
        )
        assert expected in html
    else:
        assert "<img " not in html