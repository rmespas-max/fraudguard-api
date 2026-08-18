from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_analyze_transaction_default_ai():
    payload = {
        "transaction_id": "tx_1029384",
        "account_id": "acc_88412",
        "amount": 4500.00,
        "currency": "USD",
        "country": "BO",
        "merchant_category": "electronics",
        "device_id": "dev_mac_9921"
    }
    response = client.post("/api/v1/transactions/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["transaction_id"] == "tx_1029384"
    assert data["evaluator_engine"] == "AI_Enhanced"


def test_analyze_transaction_rule_based():
    payload = {
        "transaction_id": "tx_1029384",
        "account_id": "acc_88412",
        "amount": 4500.00,
        "currency": "USD",
        "country": "BO",
        "merchant_category": "electronics",
        "device_id": "dev_mac_9921"
    }
    response = client.post("/api/v1/transactions/analyze?engine=RuleBased", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["transaction_id"] == "tx_1029384"
    assert data["evaluator_engine"] == "RuleBased"
    assert data["decision"] == "BLOCK"


def test_analyze_transaction_invalid_engine():
    payload = {
        "transaction_id": "tx_1029384",
        "account_id": "acc_88412",
        "amount": 4500.00,
        "currency": "USD",
        "country": "BO",
        "merchant_category": "electronics",
        "device_id": "dev_mac_9921"
    }
    response = client.post("/api/v1/transactions/analyze?engine=InvalidStrategy", json=payload)
    assert response.status_code == 400
    assert "Unknown evaluator engine" in response.json()["detail"]


def test_analyze_transaction_validation_error():
    # zero amount
    payload = {
        "transaction_id": "tx_1029384",
        "account_id": "acc_88412",
        "amount": 0.0,
        "currency": "USD",
        "country": "BO",
        "merchant_category": "electronics",
        "device_id": "dev_mac_9921"
    }
    response = client.post("/api/v1/transactions/analyze", json=payload)
    assert response.status_code == 422


def test_analyze_transaction_ai_fallback():
    payload = {
        "transaction_id": "fail_timeout_tx",
        "account_id": "acc_88412",
        "amount": 4500.00,
        "currency": "USD",
        "country": "BO",
        "merchant_category": "electronics",
        "device_id": "dev_mac_9921"
    }
    response = client.post("/api/v1/transactions/analyze?engine=AI_Enhanced", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["evaluator_engine"] == "RuleBased"
    assert any("Fallback triggered" in r for r in data["reasons"])


def test_analyze_transaction_internal_server_error():
    from unittest.mock import patch
    payload = {
        "transaction_id": "tx_1029384",
        "account_id": "acc_88412",
        "amount": 4500.00,
        "currency": "USD",
        "country": "BO",
        "merchant_category": "electronics",
        "device_id": "dev_mac_9921"
    }
    with patch("src.interfaces.router.AnalyzeTransactionUseCase.execute") as mock_execute:
        mock_execute.side_effect = RuntimeError("Database connection lost")
        response = client.post("/api/v1/transactions/analyze", json=payload)
        assert response.status_code == 500
        assert "Database connection lost" in response.json()["detail"]

