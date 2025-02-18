from datetime import date, timedelta

from sqlalchemy import func
from typing import List

from sqlalchemy import select
from sqlalchemy.sql import extract, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact
from src.schemas.contacts import ContactBase, ContactResponse
from src.schemas.users import User


class ContactRepository:
    def __init__(self, session: AsyncSession):
        """
        Initialize a ContactRepository.

        Args:
            session: An AsyncSession object connected to the database.
        """         
        self.db = session

    async def get_contacts(self, skip: int, limit: int, user: User) -> List[Contact]:
        """
        Retrieve a paginated list of contacts for a given user.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            user: The user who owns the contacts.

        Returns:
            A list of Contact objects.
        """
        stmt = select(Contact).filter_by(user=user).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        """
        Retrieve a specific contact by its ID.

        Args:
            contact_id: The ID of the contact.
            user: The user who owns the contact.

        Returns:
            A Contact object if found, otherwise None.
        """
        stmt = select(Contact).filter_by(id=contact_id, user=user)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactBase, user: User) -> Contact:
        """
        Create a new contact for a user.

        Args:
            body: The contact data.
            user: The user who owns the contact.

        Returns:
            The created Contact object.
        """
        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return await self.get_contact_by_id(contact.id, user)

    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        """
        Remove a contact by its ID.

        Args:
            contact_id: The ID of the contact to remove.
            user: The user who owns the contact.

        Returns:
            The removed Contact object if found, otherwise None.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactBase, user: User
    ) -> Contact | None:
        """
        Update an existing contact.

        Args:
            contact_id: The ID of the contact to update.
            body: The updated contact data.
            user: The user who owns the contact.

        Returns:
            The updated Contact object if found, otherwise None.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            for key, value in body.dict(exclude_unset=True).items():
                setattr(contact, key, value)

            await self.db.commit()
            await self.db.refresh(contact)

        return contact

    async def search_contacts(
        self, search: str, skip: int, limit: int, user: User
    ) -> List[Contact]:
        """
        Search for contacts by first name, last name, or email.

        Args:
            search: The search query string.
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            user: The user who owns the contacts.

        Returns:
            A list of matching Contact objects.
        """
        stmt = (
            select(Contact)
            .filter_by(user=user)
            .filter(
                Contact.first_name.ilike(f"%{search}%")
                | Contact.last_name.ilike(f"%{search}%")
                | Contact.email.ilike(f"%{search}%")
            )
            .offset(skip)
            .limit(limit)
        )
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_birthdays(self, days: int, user: User) -> List[Contact]:
        """
        Retrieve contacts whose birthdays fall within the next specified number of days.

        Args:
            days: The number of days to look ahead for upcoming birthdays.
            user: The user who owns the contacts.

        Returns:
            A list of Contact objects with upcoming birthdays.
        """
        today = date.today()
        future_date = today + timedelta(days=days)

        stmt = select(Contact).filter_by(user=user).filter(Contact.birthday.isnot(None))

        if today.month == future_date.month:
            stmt = stmt.filter(
                extract("month", Contact.birthday) == today.month,
                extract("day", Contact.birthday).between(today.day, future_date.day),
            )
        else:            
            stmt = stmt.filter(
                or_(
                    and_(
                        extract("month", Contact.birthday) == today.month,
                        extract("day", Contact.birthday) >= today.day,
                    ),
                    and_(
                        extract("month", Contact.birthday) == future_date.month,
                        extract("day", Contact.birthday) <= future_date.day,
                    ),
                )
            )

        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()
