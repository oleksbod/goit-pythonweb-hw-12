import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta

from src.database.models import Contact, User
from src.repository.contacts import ContactRepository
from src.schemas.contacts import ContactBase

@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def contact_repository(mock_session):
    return ContactRepository(mock_session)

@pytest.fixture
def user():
    return User(id=1, email="testuser@test.com")


@pytest.mark.asyncio
async def test_get_contacts(contact_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        Contact(id=1, first_name="John", last_name="Doe", email="john@example.com", user=user)
    ]
    mock_session.execute = AsyncMock(return_value=mock_result)

    contacts = await contact_repository.get_contacts(skip=0, limit=10, user=user)

    assert len(contacts) == 1
    assert contacts[0].first_name == "John"
    assert contacts[0].last_name == "Doe"


@pytest.mark.asyncio
async def test_get_contact_by_id(contact_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = Contact(
        id=1, first_name="John", last_name="Doe", email="john@example.com", user=user
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    contact = await contact_repository.get_contact_by_id(contact_id=1, user=user)

    assert contact is not None
    assert contact.first_name == "John"
    assert contact.email == "john@example.com"

"""
@pytest.mark.asyncio
async def test_create_contact(contact_repository, mock_session, user):
    contact_data = ContactBase(
        first_name="John",
        last_name="Doe",
        email="johndoe@example.com",
        phone="1234567890",
        birthday=date(1990, 1, 1),
        description="Test contact"
    )

    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.add = AsyncMock()
    mock_session.execute = AsyncMock(return_value=AsyncMock(scalar=AsyncMock(return_value=None)))

    created_contact = await contact_repository.create_contact(contact_data, user)

    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()

    assert created_contact is not None
    assert created_contact.first_name == contact_data.first_name
    assert created_contact.last_name == contact_data.last_name
    assert created_contact.email == contact_data.email

"""

@pytest.mark.asyncio
async def test_remove_contact(contact_repository, mock_session, user):
    contact = Contact(id=1, first_name="John", last_name="Doe", email="john@example.com", user=user)
    mock_session.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=contact)))
    mock_session.delete = AsyncMock()
    mock_session.commit = AsyncMock()

    result = await contact_repository.remove_contact(contact_id=1, user=user)

    assert result is not None
    assert result.first_name == "John"
    mock_session.delete.assert_awaited_once_with(contact)
    mock_session.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_update_contact(contact_repository, mock_session, user):    
    contact = Contact(id=1, first_name="Old", last_name="Name", email="old@example.com", user=user)

    updated_data = ContactBase(
        first_name="New",
        last_name="Name",
        email="new@example.com",
        phone="+1234567890",
        birthday="1995-05-20",
        description="Updated contact"
    )
   
    contact_repository.get_contact_by_id = AsyncMock(return_value=contact)

    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    result = await contact_repository.update_contact(contact_id=1, body=updated_data, user=user)

    assert result is not None
    assert result.first_name == "New"
    assert result.email == "new@example.com"
    assert result.phone == "+1234567890"

    contact_repository.get_contact_by_id.assert_awaited_once_with(1, user)
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()

@pytest.mark.asyncio
async def test_search_contacts(contact_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        Contact(id=1, first_name="John", last_name="Doe", email="john@example.com", user=user)
    ]
    mock_session.execute = AsyncMock(return_value=mock_result)
    
    contacts = await contact_repository.search_contacts(search="John", skip=0, limit=10, user=user)
    
    assert len(contacts) == 1
    assert contacts[0].first_name == "John"
    assert contacts[0].email == "john@example.com"

@pytest.mark.asyncio
async def test_get_birthdays(contact_repository, mock_session, user):
    today = date.today()
    future_date = today + timedelta(days=7)
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        Contact(id=1, first_name="John", last_name="Doe", email="john@example.com", birthday=today, user=user)
    ]
    mock_session.execute = AsyncMock(return_value=mock_result)
    
    contacts = await contact_repository.get_birthdays(days=7, user=user)
    
    assert len(contacts) == 1
    assert contacts[0].first_name == "John"
    assert contacts[0].birthday == today
