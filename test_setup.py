import requests
import json

BASE_URL = "http://localhost:8000"

def test_auth():
    print("=== Testing Authentication ===")
    
    response = requests.post(f"{BASE_URL}/auth/login", data={
        "username": "admin",
        "password": "admin123"
    })
    print(f"Login: {response.status_code}")
    token = response.json().get("access_token")
    print(f"Token obtained: {token[:20]}...")
    return token

def test_master_data(token):
    print("\n=== Testing Master Data ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/master-data/",
        json={
            "data_set_name": "customers",
            "data_type": "customer",
            "data_value": '{"name": "John Doe", "email": "john@example.com"}'
        },
        headers=headers
    )
    print(f"Create: {response.status_code}")
    
    response = requests.get(f"{BASE_URL}/master-data/", headers=headers)
    print(f"List: {response.status_code}, Records: {len(response.json())}")
    
    response = requests.get(f"{BASE_URL}/reports/summary", headers=headers)
    print(f"Summary: {response.status_code}")

def test_data_quality(token):
    print("\n=== Testing Data Quality ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    data = [
        {"name": "Valid User", "email": "valid@test.com"},
        {"name": "Invalid Email", "email": "not-an-email"},
    ]
    
    response = requests.post(
        f"{BASE_URL}/data-quality/import",
        json={
            "data_list": data,
            "data_set_name": "test_quality",
            "validation_rules": {
                "email": {"type": "email", "required": True},
                "name": {"type": "string", "required": True}
            }
        },
        headers=headers
    )
    result = response.json()
    print(f"Import: {response.status_code}")
    print(f"Accuracy: {result.get('accuracy')}%")

if __name__ == "__main__":
    try:
        token = test_auth()
        test_master_data(token)
        test_data_quality(token)
        print("\n=== All tests passed ===")
    except Exception as e:
        print(f"Error: {e}")