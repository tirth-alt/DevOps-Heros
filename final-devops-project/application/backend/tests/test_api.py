def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}


def test_ready_checks_database(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "READY"


def test_root_returns_app_info(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["app"] == "StockWise Inventory API"


def test_create_product(client):
    response = client.post(
        "/api/products",
        json={"name": "Wireless Mouse", "sku": "MOU-100", "category": "Peripherals",
              "quantity": 40, "price": 24.5, "reorder_level": 5},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["id"] > 0
    assert body["sku"] == "MOU-100"
    assert body["low_stock"] is False


def test_create_duplicate_sku_is_rejected(client, product):
    response = client.post("/api/products", json={"name": "Copy", "sku": product["sku"]})
    assert response.status_code == 409


def test_create_invalid_product_is_rejected(client):
    response = client.post("/api/products", json={"name": "", "sku": "X-1", "quantity": -5})
    assert response.status_code == 422


def test_list_products(client, product):
    response = client.get("/api/products")
    assert response.status_code == 200
    assert [p["sku"] for p in response.json()] == ["CAB-001"]


def test_search_and_low_stock_filters(client, product):
    client.post("/api/products", json={"name": "Desk Lamp", "sku": "LMP-1", "quantity": 2, "reorder_level": 5})
    assert [p["sku"] for p in client.get("/api/products?q=lamp").json()] == ["LMP-1"]
    assert [p["sku"] for p in client.get("/api/products?low_stock=true").json()] == ["LMP-1"]


def test_get_product_by_id(client, product):
    response = client.get(f"/api/products/{product['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "USB-C Cable"


def test_get_missing_product_returns_404(client):
    assert client.get("/api/products/9999").status_code == 404


def test_update_product(client, product):
    response = client.put(f"/api/products/{product['id']}", json={"price": 12.0, "quantity": 3})
    assert response.status_code == 200
    body = response.json()
    assert body["price"] == 12.0
    assert body["quantity"] == 3
    assert body["low_stock"] is True
    assert body["name"] == "USB-C Cable"  # unchanged fields are kept


def test_adjust_stock(client, product):
    response = client.patch(f"/api/products/{product['id']}/stock", json={"change": -5})
    assert response.status_code == 200
    assert response.json()["quantity"] == 20


def test_adjust_stock_cannot_go_negative(client, product):
    response = client.patch(f"/api/products/{product['id']}/stock", json={"change": -100})
    assert response.status_code == 400


def test_delete_product(client, product):
    assert client.delete(f"/api/products/{product['id']}").status_code == 204
    assert client.get(f"/api/products/{product['id']}").status_code == 404


def test_stats(client, product):
    client.post("/api/products", json={"name": "Monitor", "sku": "MON-1", "category": "Displays",
                                       "quantity": 2, "price": 150, "reorder_level": 3})
    body = client.get("/api/stats").json()
    assert body["total_products"] == 2
    assert body["total_units"] == 27
    assert body["inventory_value"] == round(25 * 9.99 + 2 * 150, 2)
    assert body["low_stock_count"] == 1
    assert body["categories"] == 2


def test_metrics_endpoint_exposes_prometheus_format(client):
    client.get("/health")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
