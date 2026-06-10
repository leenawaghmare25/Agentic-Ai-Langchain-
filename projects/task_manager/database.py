from app import db
from models import Task
def create_tables():
    db.create_all()
    db.session.commit()
create_tables()