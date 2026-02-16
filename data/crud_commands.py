import os, sys
try:
    # Prefer package-relative import when run with "python -m data.crud_commands"
    from .models import session, create_base as _create_base, User, Region, Condition, Request, Complaint, Taxi, User_taxi
except Exception:
    # Fallback for direct script execution (python data\crud_commands.py)
    project_root = os.path.dirname(os.path.dirname(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from data.models import session, create_base as _create_base, User, Region, Condition, Request, Complaint, Taxi, User_taxi


# ===== GENERIC CRUD FUNCTIONS =====

def add(model, **data):
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

def get(): # bitta odam olinsin.
    pass

def create_base():
    """Base yaratish uchun funksiya - agar kerak bo'lsa"""
    return _create_base()

def get_all_models_user():
    models = {
        "User": User,
        "Region": Region,
        "Condition": Condition,
        "Request": Request,
        "Complaint": Complaint,
        "Taxi": Taxi,
        "User_taxi": User_taxi}
    return session.query(User).all(), session.query(Region).all(), session.query(Condition).all(), session.query(Request).all(), session.query(Complaint).all(), session.query(Taxi).all(), session.query(User_taxi).all()

if __name__ == "__main__":
    create_base()
    # Debugging uchun o'zlashtirma
    ism=add(User, fullname="John Doeddssa", phone=1112345678901, telegram_id=119876543211)
    print(get_all_models_user())