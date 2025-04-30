from sqlalchemy.orm import Session  # type: ignore
from sqlalchemy.sql import func     # type: ignore
from model import Admin, Operator, Brand, Log
from datetime import datetime

class Admin_controller:
    def create(db: Session, code: str, first_name: str, last_name: str):
        db_admin = Admin(code=code, first_name=first_name, last_name=last_name)
        db.add(db_admin)
        db.commit()
        db.refresh(db_admin)
        return db_admin

    def get(db: Session, code: str):
        return db.query(Admin).filter(Admin.code == code).first()
    
    def get_all(db: Session):
        admins = db.query(Admin).all()
        list = [ { "code": admin.code, "first_name": admin.first_name, "last_name": admin.last_name } for admin in admins]
        list.remove({ "code": "0000", "first_name": "admin", "last_name": "admin" })
        return list

    def update(db: Session, code: str, first_name: str = None, last_name: str = None):
        db_admin = db.query(Admin).filter(Admin.code == code).first()
        if db_admin:
            if first_name:
                db_admin.first_name = first_name
            if last_name:
                db_admin.last_name = last_name
            db.commit()
            db.refresh(db_admin)
            return db_admin
        return None

    def delete(db: Session, code: str):
        db_admin = db.query(Admin).filter(Admin.code == code).first()
        if db_admin:
            db.delete(db_admin)
            db.commit()
            return True
        return False
    
class Brand_controller:
    def create(db: Session, name: str, normalized_name: str = None, language: str = "it"):
        db_brand = Brand(name=name, normalized_name=normalized_name, language=language)
        db.add(db_brand)
        db.commit()
        db.refresh(db_brand)
        return db_brand
    
    def get(db: Session, name: str):
        return db.query(Brand).filter(func.lower(Brand.name) == name.lower()).first()
    
    def get_all(db: Session):
        brands = db.query(Brand).all()
        list = [ { "name": brand.name, "normalized_name": brand.normalized_name, "language": brand.language } for brand in brands]
        list.remove({ "name": "stop", "normalized_name": None, "language": "it"})
        return list
    
    def get_list(db: Session):
        brands = db.query(Brand).all()
        return [ { f"{(brand.normalized_name if brand.normalized_name else brand.name).lower()}": f"{brand.language}" } for brand in brands]

    def get_name(db: Session, name: str):
        db_brand = db.query(Brand).filter(func.lower(Brand.name) == name.lower()).first()
        return db_brand.name
    
    def get_name_by_normalized_name(db: Session, normalized_name: str):
        db_brand = db.query(Brand).filter(func.lower(Brand.normalized_name) == normalized_name.lower()).first()
        if db_brand:
            return db_brand.name
        return None
    
    def get_language(db: Session, name: str):
        db_brand = db.query(Brand).filter(func.lower(Brand.name) == name.lower()).first()
        return db_brand.language
    
    def update(db: Session, name: str, new_normalized_name: str = None, new_language: str = None):
        db_brand = db.query(Brand).filter(Brand.name == name).first()
        if db_brand:
            if new_normalized_name is not None:
                db_brand.normalized_name = new_normalized_name
            if new_language is not None:
                db_brand.language = new_language
            db.commit()
            db.refresh(db_brand)
            return db_brand
        return None
    
    def delete(db: Session, name: str):
        db_brand = db.query(Brand).filter(Brand.name == name).first()
        if db_brand:
            db.delete(db_brand)
            db.commit()
            return True
        return False
    
class Operator_controller:
    def create(db: Session, code: str, first_name: str, last_name: str):
        db_operator = Operator(code=code, first_name=first_name, last_name=last_name)
        db.add(db_operator)
        db.commit()
        db.refresh(db_operator)
        return db_operator

    def get(db: Session, code: str):
        return db.query(Operator).filter(Operator.code == code).first()

    def get_all(db: Session):
        operators = db.query(Operator).all()
        return [ { "code": operator.code, "first_name": operator.first_name, "last_name": operator.last_name } for operator in operators]
    
    def update(db: Session, code: str, first_name: str = None, last_name: str = None, ):
        db_operator = db.query(Operator).filter(Operator.code == code).first()
        if db_operator:
            if first_name:
                db_operator.first_name = first_name
            if last_name:
                db_operator.last_name = last_name
            db.commit()
            db.refresh(db_operator)
            return db_operator
        return None

    def delete(db: Session, code: str):
        db_operator = db.query(Operator).filter(Operator.code == code).first()
        if db_operator:
            db.delete(db_operator)
            db.commit()
            return True
        return False
    
class Log_controller:
    def create(db: Session, code: str, brand: str, cart: int):
        db_log = Log(operator_code=code, brand_name=brand, cart=cart)
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log

    def get_logs(db: Session, operator_code: str = None, day: str = None):
        query = db.query(Log)
        
        if operator_code:
            query = query.filter(Log.operator_code == operator_code)
        
        if day:
            day_start = datetime.strptime(day, "%Y-%m-%d")
            day_end = day_start.replace(hour=23, minute=59, second=59, microsecond=999999)
            query = query.filter(Log.timestamp >= day_start, Log.timestamp <= day_end)
        
        logs = query.all()
        return [{ "id": f"{log.id}", "operator_code": log.operator_code, "brand_name": log.brand_name, "cart": f"{log.cart}", "timestamp": f"{log.timestamp}" } for log in logs]