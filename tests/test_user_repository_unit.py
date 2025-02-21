import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, UserRole
from src.repository.users import UserRepository
from src.schemas.users import UserCreate


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def user_repository(mock_session):
    return UserRepository(mock_session)


@pytest.fixture
def user_create_data():
    return UserCreate(
        username="testuser",
        email="testuser@example.com",
        password="password123",
        role=UserRole.USER
    )


@pytest.mark.asyncio
async def test_get_user_by_id(user_repository, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(id=1, username="testuser", email="testuser@example.com")
    mock_session.execute = AsyncMock(return_value=mock_result)

    user = await user_repository.get_user_by_id(user_id=1)

    assert user is not None
    assert user.id == 1
    assert user.username == "testuser"
    assert user.email == "testuser@example.com"


@pytest.mark.asyncio
async def test_get_user_by_email(user_repository, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(id=1, username="testuser", email="testuser@example.com")
    mock_session.execute = AsyncMock(return_value=mock_result)

    user = await user_repository.get_user_by_email(email="testuser@example.com")

    assert user is not None
    assert user.email == "testuser@example.com"
    assert user.username == "testuser"


@pytest.mark.asyncio
async def test_create_user(user_repository, mock_session, user_create_data):
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    created_user = await user_repository.create_user(user_create_data)

    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()

    assert created_user is not None
    assert created_user.username == user_create_data.username
    assert created_user.email == user_create_data.email


@pytest.mark.asyncio
async def test_update_avatar_url(user_repository, mock_session):
    user = User(id=1, username="testuser", email="testuser@example.com", avatar="old-avatar-url")
    mock_session.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=user)))
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    updated_user = await user_repository.update_avatar_url(email="testuser@example.com", url="new-avatar-url")

    assert updated_user is not None
    assert updated_user.avatar == "new-avatar-url"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_confirmed_email(user_repository, mock_session):
    user = User(id=1, username="testuser", email="testuser@example.com", confirmed=False)
    mock_session.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=user)))
    mock_session.commit = AsyncMock()

    await user_repository.confirmed_email(email="testuser@example.com")

    assert user.confirmed is True
    mock_session.commit.assert_awaited_once()
