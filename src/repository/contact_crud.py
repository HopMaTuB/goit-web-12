from sqlalchemy.future import select
from sqlalchemy.orm import Session
from settings import limiter
from src.configuration import models
from src import schemas

async def create_contact(db: Session, contact: schemas.ContactCreate):
    """
    Create a new contact in the database.

    Args:
        db (AsyncSession): The database session.
        contact (schemas.ContactCreate): The contact data to create.

    Returns:
        models.Contact: The created contact object.
    """
    db_contact = models.Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


async def get_contact(db: Session, contact_id: int):
    """
    Retrieve a contact by its ID.

    Args:
        db (AsyncSession): The database session.
        contact_id (int): The ID of the contact to retrieve.

    Returns:
        Optional[models.Contact]: The contact object if found, else None.
    """
    result =  db.execute(select(models.Contact).filter(models.Contact.id == contact_id))
    return result.scalar_one_or_none()

async def get_contacts(db: Session):
    """
    Retrieve all contacts from the database.

    Args:
        db (AsyncSession): The database session.

    Returns:
        List[models.Contact]: A list of all contact objects.
    """
    result = db.execute(select(models.Contact))
    return result.scalars().all()

async def update_contact(db: Session, contact_id: int, contact: schemas.ContactUpdate):
    """
    Update an existing contact in the database.

    Args:
        db (AsyncSession): The database session.
        contact_id (int): The ID of the contact to update.
        contact (schemas.ContactUpdate): The updated contact data.

    Returns:
        Optional[models.Contact]: The updated contact object if found, else None.
    """
    db_contact = await get_contact(db, contact_id)
    if db_contact is None:
        return None
    for key, value in contact.dict().items():
        setattr(db_contact, key, value)
    db.commit()
    db.refresh(db_contact)
    return db_contact

async def delete_contact(db: Session, contact_id: int):
    """
    Delete a contact from the database.

    Args:
        db (AsyncSession): The database session.
        contact_id (int): The ID of the contact to delete.

    Returns:
        Optional[models.Contact]: The deleted contact object if found, else None.
    """
    db_contact = await get_contact(db, contact_id)
    if db_contact is None:
        return None
    db.delete(db_contact)
    db.commit()
    return db_contact
