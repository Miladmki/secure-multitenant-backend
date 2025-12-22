from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, text, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    tenant = relationship("Tenant", back_populates="users")
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("email", "tenant_id", name="uq_user_email_tenant"),
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
