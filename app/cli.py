import typer
from app.database import create_db_and_tables, get_cli_session, drop_all
from app.models import *
from fastapi import Depends
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from app.models.animal import Animal
from app.models.user import User, UserBase

cli = typer.Typer()

@cli.command()
def initialize():
    with get_cli_session() as db:
        drop_all() 
        create_db_and_tables() 
        
        bob = UserBase(username='bob', email='bob@mail.com', password="bobpass")
        bob_db = User.model_validate(bob)
        db.add(bob_db)
        for i in range (5):
            animal = Animal(kingdom="Animalia", phylum="Chordata", classTaxonomic="Mammalia", order="Carnivora", family="Felidae", genus="Panthera", species="Leo")
            animal_db = Animal.model_validate(animal)
            db.add(animal_db)            
        db.commit()
        ##############################
        print("Database Initialized")