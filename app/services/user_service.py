from sqlalchemy.orm import Session
from app.models.user import User


def list_users(db: Session, tenant_id: int):
    """
    لیست همه کاربران یک tenant خاص
    """
    return db.query(User).filter(User.tenant_id == tenant_id).all()


def get_user_by_id(db: Session, user_id: int, tenant_id: int) -> User | None:
    """
    گرفتن یک کاربر خاص از tenant مشخص
    """
    return (
        db.query(User).filter(User.id == user_id, User.tenant_id == tenant_id).first()
    )


def create_user(db: Session, email: str, hashed_password: str, tenant_id: int) -> User:
    """
    ایجاد کاربر جدید در tenant مشخص
    """
    user = User(email=email, hashed_password=hashed_password, tenant_id=tenant_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user_email(
    db: Session, user_id: int, tenant_id: int, email: str
) -> User | None:
    """
    آپدیت ایمیل کاربر در tenant مشخص
    """
    user = get_user_by_id(db, user_id, tenant_id)
    if not user:
        return None
    user.email = email
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int, tenant_id: int) -> bool:
    """
    حذف کاربر در tenant مشخص
    """
    user = get_user_by_id(db, user_id, tenant_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True
