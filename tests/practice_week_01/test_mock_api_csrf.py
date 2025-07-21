import pytest

def fetch_data(headers=None):
    if headers and headers.get("X-CSRF-Token") == "valid-token":
        return {"status": "success"}
    raise PermissionError("Invalid or missing CSRF token")

def test_api_with_valid_token():
    headers = {"X-CSRF-Token": "valid-token"}
    response = fetch_data(headers)
    assert response["status"] == "success"

def test_api_without_token():
    with pytest.raises(PermissionError):
        fetch_data()

def test_api_with_invalid_token():
    with pytest.raises(PermissionError):
        fetch_data({"X-CSRF-Token": "wrong-token"})
