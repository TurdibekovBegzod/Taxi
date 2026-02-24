import os, sys
try:
    # Prefer package-relative import when run with "python -m data.crud_commands"
    from .models import session, User
except Exception:
    # Fallback for direct script execution (python data\crud_commands.py)
    project_root = os.path.dirname(os.path.dirname(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from data.models import session, User, Base

from sqlalchemy.orm import Session
# ===== GENERIC CRUD FUNCTIONS =====

def add(model, data):
    obj = model(**data)
    session.add(obj)
    session.commit()
    return obj



def update(model, filters: dict, updates: dict):
    obj = session.query(model).filter_by(**filters).first()
    if obj:
        for k, v in updates.items():
            setattr(obj, k, v)
        session.commit()
        return obj


def delete(model, **filters):
    obj = session.query(model).filter_by(**filters).first()
    if obj:
        session.delete(obj)
        session.commit()
        return True
    return False

def get(model, filters : dict): # bitta odam olinsin.
    obj = session.query(model).filter_by(**filters).first()

    return obj
    




if __name__ == "__main__":
    # Debugging uchun o'zlashtirma
    ism=add(User, fullname="John Doeddssa", phone=1112345678901, telegram_id=119876543211)
    