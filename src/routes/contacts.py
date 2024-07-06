from fastapi import APIRouter, Depends, HTTPException,Request
from sqlalchemy.orm import Session
from src.configuration import database,models
from src.repository import contact_crud
from src.repository.auth import get_current_user
from src.configuration.models import User
from src import schemas
from sqlalchemy import select
from datetime import datetime,timedelta
from settings import limiter



router_contacts = APIRouter()

@router_contacts.post("/contacts/", response_model=schemas.Contact,status_code=201)
@limiter.limit('5/minute')
async def create_contact(request: Request,contact: schemas.ContactCreate, db: Session = Depends(database.get_db), user: User=Depends(get_current_user)):
    return await contact_crud.create_contact(db=db, contact=contact)

@router_contacts.get("/contacts/", response_model=list[schemas.Contact])
@limiter.limit('5/minute')
async def read_contacts(request: Request,db: Session = Depends(database.get_db), user: User=Depends(get_current_user)):
    contacts = await contact_crud.get_contacts(db=db)
    return contacts

@router_contacts.get("/contacts/{contact_id}")
@limiter.limit('5/minute')
async def read_contact(request: Request,contact_id: int, db: Session = Depends(database.get_db), user: User=Depends(get_current_user)):
    db_contact = await contact_crud.get_contact(db=db, contact_id=contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

@router_contacts.put("/contacts/{contact_id}", response_model=schemas.Contact)
@limiter.limit('5/minute')
async def update_contact(request: Request,contact_id: int, contact: schemas.ContactUpdate, db: Session = Depends(database.get_db), user: User=Depends(get_current_user)):
    db_contact = await contact_crud.update_contact(db=db, contact_id=contact_id, contact=contact)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

@router_contacts.delete("/contacts/{contact_id}", response_model=schemas.Contact)
@limiter.limit('5/minute')
async def delete_contact(request: Request,contact_id: int, db: Session = Depends(database.get_db), user: User=Depends(get_current_user)):
    db_contact = await contact_crud.delete_contact(db=db, contact_id=contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@router_contacts.get("/contacts/search/", response_model=list[schemas.Contact])
@limiter.limit('5/minute')
async def search_contacts(request: Request,query: str, db: Session = Depends(database.get_db), user: User=Depends(get_current_user)):
    query = f"%{query}%"
    result = db.execute(
        select(models.Contact).filter(
            (models.Contact.first_name.ilike(query)) |
            (models.Contact.last_name.ilike(query)) |
            (models.Contact.email.ilike(query))
        )
    )
    return result.scalars().all()

@router_contacts.get("/contacts/upcoming_birthdays/", response_model=list[schemas.Contact])
@limiter.limit('5/minute')
async def upcoming_birthdays(request: Request,db: Session = Depends(database.get_db), user: User=Depends(get_current_user)):
    today = datetime.today().date()
    next_week = today + timedelta(days=7)
    result = db.execute(
        select(models.Contact).filter(
            models.Contact.birth_date.between(today, next_week)
        )
    )
    return result.scalars().all()
