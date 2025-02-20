import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import User, Contact
from src.services.auth import create_access_token
from tests.conftest import TestingSessionLocal
from datetime import datetime, timedelta

contact_data = {"first_name": "John", "role":"user", "last_name": "Doe", "email": "john.doe@example.com", "phone": "1234567890", "birthday": datetime(2010,1,1).isoformat(), "description":"Test contact"}

@pytest.mark.asyncio
async def test_create_contact(client: TestClient, get_token: str):   
    headers = {"Authorization": f"Bearer {get_token}"}
    response = client.post("/api/contacts", json=contact_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == contact_data["first_name"]
    assert data["email"] == contact_data["email"]
    assert data["phone"] == contact_data["phone"]

@pytest.mark.asyncio
async def test_read_contacts(client: TestClient, get_token: str):    
    headers = {"Authorization": f"Bearer {get_token}"}
    response = client.post("/api/contacts", json=contact_data, headers=headers)
    assert response.status_code == 201
    contact_id = response.json()["id"]
   
    response = client.get(f"/api/contacts/{contact_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == contact_data["first_name"]
    assert data["email"] == contact_data["email"]
    assert data["phone"] == contact_data["phone"]

@pytest.mark.asyncio
async def test_update_contact(client: TestClient, get_token: str):    
    headers = {"Authorization": f"Bearer {get_token}"}
    response = client.post("/api/contacts", json=contact_data, headers=headers)
    assert response.status_code == 201
    contact_id = response.json()["id"]

    updated_data = {"first_name": "Jane","last_name": "Doe", "email": "jane.doe@example.com", "phone": "0987654321", "birthday": str(datetime(2010,1,1)), "description":"Test contact"}
    
    response = client.put(f"/api/contacts/{contact_id}", json=updated_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == updated_data["first_name"]
    assert data["email"] == updated_data["email"]
    assert data["phone"] == updated_data["phone"]

@pytest.mark.asyncio
async def test_delete_contact(client: TestClient, get_token: str):    
    headers = {"Authorization": f"Bearer {get_token}"}
    response = client.post("/api/contacts/", json=contact_data, headers=headers)
    assert response.status_code == 201
    contact_id = response.json()["id"]
    
    response = client.delete(f"/api/contacts/{contact_id}", headers=headers)
    assert response.status_code == 204
    
    response = client.get(f"/api/contacts/{contact_id}", headers=headers)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Contact not found"

"""
@pytest.mark.asyncio
async def test_search_contacts(client: TestClient, get_token: str):    
    headers = {"Authorization": f"Bearer {get_token}"}
    response = client.post("/api/contacts", json=contact_data, headers=headers)
    assert response.status_code == 201
    contact_id = response.json()["id"]

    
    search_query = "ohn"
    response = client.get(f"/api/contacts/search?text={search_query}&skip=0&limit=100", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0  

"""

@pytest.mark.asyncio
async def test_get_birthdays(client: TestClient, get_token: str):
    future_date = datetime.now() + timedelta(days=2)
    past_date = future_date.replace(year=future_date.year - 10)
    contact_data_with_birthday = {**contact_data, "birthday": str(past_date)}
    headers = {"Authorization": f"Bearer {get_token}"}
    response = client.post("/api/contacts", json=contact_data_with_birthday, headers=headers)
    assert response.status_code == 201
    
    response = client.post("/api/contacts/birthdays", json={"days": 10}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0  
