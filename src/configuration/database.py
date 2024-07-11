from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from settings import SQLALCHEMY_DATABASE_URL,SQLALCHEMY_TEST_DATABASE_URL



engine = create_engine(
    SQLALCHEMY_DATABASE_URL,echo=True
)

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,echo=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db(is_test: bool = False):
    if is_test:
        db = TestSessionLocal
    else:
        db = SessionLocal()
    try:
        yield db
    finally:
        db.close()