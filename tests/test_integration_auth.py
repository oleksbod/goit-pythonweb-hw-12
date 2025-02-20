from unittest.mock import Mock

import pytest
from sqlalchemy import select

from src.database.models import User
from tests.conftest import TestingSessionLocal

user_data = {"username": "agent007", "email": "agent007@gmail.com", "password": "12345678", "role": "user"}

def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "hashed_password" not in data
    assert "avatar" in data

def test_repeat_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Користувач з таким email вже існує"

def test_not_confirmed_login(client):
    response = client.post("api/auth/login",
                           json={"email": user_data.get("email"), "password": user_data.get("password")})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Електронна адреса не підтверджена"

@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).where(User.email == user_data.get("email")))
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post("api/auth/login",
                           json={"email": user_data.get("email"), "password": user_data.get("password")})
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data

def test_wrong_password_login(client):
    response = client.post("api/auth/login",
                           json={"email": user_data.get("email"), "password": "password"})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Неправильний логін або пароль"

def test_wrong_email_login(client):
    response = client.post("api/auth/login",
                           json={"email": "email", "password": user_data.get("password")})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Неправильний логін або пароль"

def test_validation_error_login(client):
    response = client.post("api/auth/login",
                           data={"password": user_data.get("password")})
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data

def test_email_confirmation(client, get_token):
    token = get_token
    response = client.get(f"api/auth/confirmed_email/{token}")
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == "Ваша електронна пошта вже підтверджена"

def test_request_email_confirmation(client):
    response = client.post("api/auth/request_email", json={"email": user_data.get("email")})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Ваша електронна пошта вже підтверджена"

def test_request_email_when_already_confirmed(client):
    # Assuming the user has already confirmed their email.
    response = client.post("api/auth/request_email", json={"email": user_data.get("email")})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Ваша електронна пошта вже підтверджена"

def test_reset_password(client, monkeypatch):
    mock_send_reset_email = Mock()
    monkeypatch.setattr("src.api.auth.send_reset_password_email", mock_send_reset_email)
    
    response = client.post("api/auth/reset_password", json={"email": user_data.get("email")})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Перевірте вашу електронну пошту для скидання пароля"

def test_reset_password_for_nonexistent_user(client):
    response = client.post("api/auth/reset_password", json={"email": "nonexistent_email@gmail.com"})
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Користувача не знайдено"

def test_change_password(client, get_token):
    reset_token = get_token
    new_password = "newpassword123"
    
    response = client.post("api/auth/change_password", json={"token": reset_token, "new_password": new_password})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Пароль успішно змінено"

def test_invalid_change_password_token(client, get_token):
    reset_token = get_token+"invalid"
    new_password = "newpassword123"
    
    response = client.post("api/auth/change_password", json={"token": reset_token, "new_password": new_password})
    assert response.status_code == 422, response.text
    data = response.json()
    assert data["detail"] == "Невірний токен для перевірки електронної пошти"

def test_invalid_refresh_token(client):
    refresh_token = "<invalid_refresh_token>"
    
    response = client.post("api/auth/refresh-token", json={"refresh_token": refresh_token})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid or expired refresh token"