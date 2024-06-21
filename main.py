from fastapi import FastAPI
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from src.configuration import models
from src.repository import contact_crud
from src import schemas
from src.configuration import database
from sqlalchemy import select
from fastapi import status
from src.routes.users import router as user_router
from src.routes.contacts import router_contacts as contact_router


app = FastAPI()
app.include_router(user_router, prefix='/api')
app.include_router(contact_router, prefix='/api')

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)