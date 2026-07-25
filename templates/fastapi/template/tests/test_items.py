from fastapi.testclient import TestClient


def test_create_and_get_item(client: TestClient) -> None:
    created = client.post("/items", json={"name": "widget", "quantity": 3})
    assert created.status_code == 201
    item = created.json()

    fetched = client.get(f"/items/{item['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "widget"


def test_get_missing_item_is_404(client: TestClient) -> None:
    response = client.get("/items/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_create_rejects_negative_quantity(client: TestClient) -> None:
    response = client.post("/items", json={"name": "widget", "quantity": -1})
    assert response.status_code == 422
