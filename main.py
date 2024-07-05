from fastapi import FastAPI
from fastapi import FastAPI
from src.routes.users import router as user_router
from src.routes.contacts import router_contacts as contact_router
from src.routes.auth import router as auth_router


app = FastAPI()
# app.include_router(user_router, prefix='/api')
app.include_router(auth_router, prefix='/api')
app.include_router(contact_router, prefix='/api')


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)