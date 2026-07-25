import pytest
from httpx2 import AsyncClient

pytestmark = pytest.mark.anyio


async def test_create_and_get_item(client: AsyncClient) -> None:
    created = await client.post("/items", json={"name": "widget", "quantity": 3})
    assert created.status_code == 201
    item = created.json()

    fetched = await client.get(f"/items/{item['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "widget"


async def test_get_missing_item_is_404(client: AsyncClient) -> None:
    response = await client.get("/items/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


async def test_create_rejects_negative_quantity(client: AsyncClient) -> None:
    response = await client.post("/items", json={"name": "widget", "quantity": -1})
    assert response.status_code == 422


async def test_each_app_gets_an_isolated_repository(client: AsyncClient) -> None:
    assert (await client.get("/items")).json() == []


async def test_list_items_validates_pagination(client: AsyncClient) -> None:
    response = await client.get("/items?limit=101")

    assert response.status_code == 422
