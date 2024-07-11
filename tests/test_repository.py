import sys
import os

# Добавьте корневую директорию вашего проекта в PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import unittest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src import schemas
from src.repository.contact_crud import create_contact, get_contact, get_contacts, update_contact, delete_contact

DATABASE_URL = "sqlite+aiosqlite:///test.db"

Base = declarative_base()

class TestContactFunctions(unittest.TestCase):

    @pytest.mark.asyncio
    async def asyncSetUp(self):
        self.engine = create_async_engine(DATABASE_URL, echo=True)
        self.async_session = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.session = self.async_session()

    @pytest.mark.asyncio
    async def asyncTearDown(self):
        await self.session.close()
        await self.engine.dispose()
        if os.path.exists("test.db"):
            os.remove("test.db")

    @pytest.mark.asyncio
    async def test_create_contact(self):
        contact_data = schemas.ContactCreate(name="John Doe", email="john.doe@example.com")
        new_contact = await create_contact(self.session, contact_data)
        self.assertEqual(new_contact.name, "John Doe")
        self.assertEqual(new_contact.email, "john.doe@example.com")

    @pytest.mark.asyncio
    async def test_get_contact(self):
        contact_data = schemas.ContactCreate(name="Jane Doe", email="jane.doe@example.com")
        new_contact = await create_contact(self.session, contact_data)
        contact = await get_contact(self.session, new_contact.id)
        self.assertIsNotNone(contact)
        self.assertEqual(contact.name, "Jane Doe")
        self.assertEqual(contact.email, "jane.doe@example.com")

    @pytest.mark.asyncio
    async def test_get_contacts(self):
        contact_data1 = schemas.ContactCreate(name="John Doe", email="john.doe@example.com")
        contact_data2 = schemas.ContactCreate(name="Jane Doe", email="jane.doe@example.com")
        await create_contact(self.session, contact_data1)
        await create_contact(self.session, contact_data2)
        contacts = await get_contacts(self.session)
        self.assertEqual(len(contacts), 2)

    @pytest.mark.asyncio
    async def test_update_contact(self):
        contact_data = schemas.ContactCreate(name="John Doe", email="john.doe@example.com")
        new_contact = await create_contact(self.session, contact_data)
        update_data = schemas.ContactUpdate(name="John Smith", email="john.smith@example.com")
        updated_contact = await update_contact(self.session, new_contact.id, update_data)
        self.assertEqual(updated_contact.name, "John Smith")
        self.assertEqual(updated_contact.email, "john.smith@example.com")

    @pytest.mark.asyncio
    async def test_delete_contact(self):
        contact_data = schemas.ContactCreate(name="Jane Doe", email="jane.doe@example.com")
        new_contact = await create_contact(self.session, contact_data)
        deleted_contact = await delete_contact(self.session, new_contact.id)
        self.assertIsNotNone(deleted_contact)
        contact = await get_contact(self.session, new_contact.id)
        self.assertIsNone(contact)

if __name__ == "__main__":
    unittest.main()