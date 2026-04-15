import logging
import requests
from datetime import datetime, timezone, timedelta
from sqlmodel import SQLModel, Session, create_engine, select, func
from typing import Annotated
from fastapi import Depends
from app.config import get_settings
from app.models.user import *
from app.models.animal import Animal
from app.models.user_animal import UserAnimal
from contextlib import contextmanager
from app.utilities.security import encrypt_password

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
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

@contextmanager
def get_cli_session():
    yield from _session_generator()
    
def get_animals(): #works!! Yippee
    with get_cli_session() as db:
        try:
            #want to populate wiki page with animal photos
            url = "https://api.inaturalist.org/v1/taxa?rank=species&per_page=200"
            data = requests.get(url, timeout=30).json()
            
            inaturalist_data = [
                {
                    "species": item["name"],
                    "preferred_common_name": item["preferred_common_name"],
                    "photo_url": item.get("default_photo", {}).get("url")
                }
                for item in data["results"]
                if 1 in item.get('ancestor_ids', [])
            ]
            
            animals_added = 0
            for animal in inaturalist_data:
                try:
                    taxonomic_url = f"https://api.gbif.org/v1/species/match?name={animal['species']}"
                    resp = requests.get(taxonomic_url, timeout=10).json()
                    taxonomic_data = {
                        "kingdom": resp.get("kingdom", "Unknown"),
                        "phylum": resp.get("phylum", "Unknown"),
                        "class": resp.get("class", "Unknown"),
                        "order": resp.get("order", "Unknown"),
                        "family": resp.get("family", "Unknown"),
                        "genus": resp.get("genus", "Unknown")
                    }
                    animal.update(taxonomic_data)
                    
                    if not db.exec(select(Animal).where(Animal.species == animal["species"])).first():
                        new_animal = Animal(
                            kingdom=animal.get("kingdom", "Unknown"),
                            phylum=animal.get("phylum", "Unknown"),
                            class_=animal.get("class", "Unknown"),
                            order=animal.get("order", "Unknown"),
                            family=animal.get("family", "Unknown"),
                            species=animal.get("species", "Unknown"),
                            common_name=animal.get("preferred_common_name", "Unknown"),
                            pic=animal.get("photo_url", "Unknown")
                        )
                        db.add(new_animal)
                        animals_added += 1
                except Exception as e:
                    logger.warning(f"Failed to process animal {animal.get('species', 'unknown')}: {e}")
                    continue
            
            db.commit()
            print(f"Successfully added {animals_added} animals to database.")
            
        except Exception as e:
            logger.error(f"Failed to fetch animal data: {e}")
            db.rollback()

def add_user_animal(user, genus, species, img_b64):
    with get_cli_session() as db:
        find_animal = db.exec(select(Animal).where(Animal.species.like("%"+species))).first()
        if not find_animal:
            try:
                url = f"https://api.inaturalist.org/v1/taxa?rank=species&q={genus}+{species}"
                response = requests.get(url, timeout=30).json()
                results = response.get("results")
                if isinstance(results, list) and results:
                    result = results[0]
                    if 1 in result.get('ancestor_ids', []):
                        animal = {
                            "species": result.get("name"),
                            "preferred_common_name": result.get("preferred_common_name"),
                            "photo_url": result.get("default_photo", {}).get("url")
                        }
                    else:
                        animal = None
                else:
                    animal = None

                if animal:
                    try:
                        taxonomic_url = f"https://api.gbif.org/v1/species/match?name={animal['species']}"
                        resp = requests.get(taxonomic_url, timeout=10).json()
                        taxonomic_data = {
                            "kingdom": resp.get("kingdom", "Unknown"),
                            "phylum": resp.get("phylum", "Unknown"),
                            "class": resp.get("class", "Unknown"),
                            "order": resp.get("order", "Unknown"),
                            "family": resp.get("family", "Unknown"),
                            "genus": resp.get("genus", "Unknown")
                        }
                        animal.update(taxonomic_data)

                        find_animal = Animal(
                            kingdom=animal.get("kingdom", "Unknown"),
                            phylum=animal.get("phylum", "Unknown"),
                            class_=animal.get("class", "Unknown"),
                            order=animal.get("order", "Unknown"),
                            family=animal.get("family", "Unknown"),
                            species=animal.get("species", "Unknown"),
                            common_name=animal.get("preferred_common_name", "Unknown"),
                            pic=animal.get("photo_url", "Unknown")
                        )
                        db.add(find_animal)
                        db.commit()
                        db.refresh(find_animal)
                        print(f"Successfully added new animal to database.")
                    except Exception as e:
                        logger.warning(f"Failed to process animal {animal.get('species', 'unknown')}: {e}")
                        db.rollback()
            except Exception as e:
                logger.error(f"Failed to fetch animal data: {e}")
                db.rollback()

        if find_animal:
            existing = db.exec(select(UserAnimal).where(UserAnimal.user_id == user.id, UserAnimal.animal_id == find_animal.animal_id)).first()
            if not existing:
                user_animal = UserAnimal(user_id=user.id, animal_id=find_animal.animal_id, user_pic=img_b64)
                db.add(user_animal)
                db.commit()
            db.refresh(find_animal)
            return find_animal
        return None

def seed_demo_users(db):
    demo_users = [
        {"username": "john", "email": "john@test.mail", "password": "1234", "points": 1},
        {"username": "alice", "email": "alice@test.mail", "password": "1234", "points": 3},
        {"username": "charlie", "email": "charlie@test.mail", "password": "1234", "points": 5}
    ]
    
    animals = db.exec(select(Animal).limit(10)).all()
    if not animals:
        return

    for demo in demo_users:
        user = db.exec(select(User).where(User.username == demo["username"])).first()
        if not user:
            user = User(username=demo["username"], email=demo["email"], password=encrypt_password(demo["password"]))
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created demo user {demo['username']}")

        current_count = db.exec(select(UserAnimal).where(UserAnimal.user_id == user.id)).all()
        if len(current_count) >= demo["points"]:
            continue

        logs_needed = demo["points"] - len(current_count)
        for index in range(logs_needed):
            selected_animal = animals[index % len(animals)]
            date_offset = timedelta(days=index)
            date_added = datetime.now(timezone(timedelta(hours=-4))) - date_offset
            user_animal = UserAnimal(
                user_id=user.id,
                animal_id=selected_animal.animal_id,
                user_pic="seeded",
                date_added=date_added,
                date_added_str=date_added.strftime("%d/%m/%y")
            )
            db.add(user_animal)
        db.commit()
        print(f"Added {logs_needed} weekly logs for {demo['username']}")


def init():
    create_db_and_tables()    
    with get_cli_session() as db:
        if not db.exec(select(Admin).where(Admin.username == "bob")).first():
            admin = Admin(username="bob", email="bob@test.mail", password=encrypt_password("1234"))
            db.add(admin)
            db.commit()
            print("Admin user created.")

        seed_demo_users(db)

        if not db.exec(select(Animal)).first():
            print("Database empty! Fetching data.")
            get_animals()
        else:
            print("Animals already stored in db.")
