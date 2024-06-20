from sqlalchemy.future import select
from sqlalchemy.orm import Session

from src.configuration import models
from src import schemas

async def create_contact(db: Session, contact: schemas.ContactCreate):
    db_contact = models.Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


async def get_contact(db: Session, contact_id: int):
    result =  db.execute(select(models.Contact).filter(models.Contact.id == contact_id))
    return result.scalar_one_or_none()

async def get_contacts(db: Session):
    result = db.execute(select(models.Contact))
    return result.scalars().all()

async def update_contact(db: Session, contact_id: int, contact: schemas.ContactUpdate):
    db_contact = await get_contact(db, contact_id)
    if db_contact is None:
        return None
    for key, value in contact.dict().items():
        setattr(db_contact, key, value)
    db.commit()
    db.refresh(db_contact)
    return db_contact

async def delete_contact(db: Session, contact_id: int):
    db_contact = await get_contact(db, contact_id)
    if db_contact is None:
        return None
    db.delete(db_contact)
    db.commit()
    return db_contact
