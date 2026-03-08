from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Contact(Base):
    __tablename__ = "contacts"
    __table_args__ = (
        CheckConstraint(
            "link_precedence IN ('primary', 'secondary')",
            name="contacts_link_precedence_check",
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_number = Column(Text, nullable=True)
    email = Column(Text, nullable=True)
    linked_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)
    link_precedence = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    linked_contact = relationship("Contact", remote_side=[id], foreign_keys=[linked_id])
