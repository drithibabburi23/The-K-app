def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_basic_catalogue_flow(client):
    user = client.post(
        "/api/v1/users",
        json={"name": "Asha", "role": "artisan", "language": "en"},
    )
    category = client.post(
        "/api/v1/categories",
        json={"name": "Baskets", "description": "Handwoven baskets"},
    )

    assert user.status_code == 201
    assert category.status_code == 201

    product = client.post(
        "/api/v1/products",
        json={
            "title": "Palm basket",
            "description": "A handwoven basket",
            "material": "Palm leaf",
            "craft_type": "Weaving",
            "price": "450.00",
            "language": "en",
            "status": "published",
            "artisan_id": user.json()["id"],
            "category_id": category.json()["id"],
        },
    )

    assert product.status_code == 201
    assert product.json()["title"] == "Palm basket"

    products = client.get("/api/v1/products")
    assert products.status_code == 200
    assert len(products.json()) == 1


def test_missing_resource_returns_404(client):
    response = client.get("/api/v1/products/999")

    assert response.status_code == 404
    assert "was not found" in response.json()["detail"]
