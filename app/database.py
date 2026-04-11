import logging
import requests
from sqlmodel import SQLModel, Session, create_engine
from app.config import get_settings
from app.models.user import *
from contextlib import contextmanager

logger = logging.getLogger(__name__)

engine = create_engine(
    get_settings().database_uri, 
    echo=get_settings().env.lower() in ["dev", "development", "test", "testing", "staging"],
    pool_size=get_settings().db_pool_size,
    max_overflow=get_settings().db_additional_overflow,
    pool_timeout=get_settings().db_pool_timeout,
    pool_recycle=get_settings().db_pool_recycle,
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def drop_all():
    SQLModel.metadata.drop_all(bind=engine)
    
def _session_generator():
    with Session(engine) as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

def get_session():
    yield from _session_generator()

@contextmanager
def get_cli_session():
    yield from _session_generator()

def init():
    drop_all()
    create_db_and_tables()
    with get_cli_session() as db:
        admin_tester = Admin(username="bob", email="bob@test.mail", password="1234")
        db.add(admin_tester)
        db.commit()
        
        # #trying a thing tbh
        # url = "https://api.inaturalist.org/v1/taxa?rank=species&per_page=200"
        # data = requests.get(url).json()
        
        # inaturalist_data = [
        #     item for item in data.get('results', []) 
        #     if 1 in item.get('ancestor_ids', [])
        # ]
        
        # print (inaturalist_data[0])
        