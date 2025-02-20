from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas.contacts import ContactBase, ContactResponse, ContactBirthdayRequest
from src.schemas.users import User
from src.services.auth import get_current_user 
from src.services.contacts import ContactService

router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.get("/", response_model=List[ContactResponse], status_code=status.HTTP_200_OK)
async def read_contacts(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
):
    """
    Retrieve a list of contacts with pagination.

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        db: Database session.
        user: The authenticated user.

    Returns:
        A list of contact objects.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(skip, limit, user)
    return contacts

@router.get("/{contact_id}", response_model=ContactBase)
async def read_contact(contact_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Retrieve a specific contact by its ID.

    Args:
        contact_id: The ID of the contact.
        db: Database session.
        user: The authenticated user.

    Returns:
        The contact object if found, otherwise raises HTTP 404.
    """
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact

@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactBase, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Create a new contact.

    Args:
        body: The contact details.
        db: Database session.
        user: The authenticated user.

    Returns:
        The newly created contact object.
    """
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, user)

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactBase, contact_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
):
    """
    Update an existing contact.

    Args:
        contact_id: The ID of the contact to update.
        body: The updated contact data.
        db: Database session.
        user: The authenticated user.

    Returns:
        The updated contact object if found, otherwise raises HTTP 404.
    """
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact

@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_contact(contact_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Remove a contact by its ID.

    Args:
        contact_id: The ID of the contact to remove.
        db: Database session.
        user: The authenticated user.

    Returns:
        None if the contact is removed, otherwise raises HTTP 404.
    """
    contact_service = ContactService(db)
    contact = await contact_service.remove_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return

@router.get("/search", response_model=List[ContactResponse])
async def search_contacts(
    text: str, skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
):    
    """
    Search for contacts by first name, last name, or email.

    Args:
        text: The search query.
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        db: Database session.
        user: The authenticated user.

    Returns:
        A list of matching contacts.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.search_contact(text, skip, limit, user)
    return contacts

@router.post("/birthdays", response_model=List[ContactResponse])
async def get_birthdays(
    body: ContactBirthdayRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
):
    """
    Retrieve contacts with upcoming birthdays.

    Args:
        body: The request containing the number of days ahead to check.
        db: Database session.
        user: The authenticated user.

    Returns:
        A list of contacts whose birthdays are within the specified range.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_birthdays(body.days, user)
    return contacts
