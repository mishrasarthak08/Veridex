from sqlalchemy import Column, String, Uuid, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.types import TypeDecorator, String as SQLString
from app.db.models.base import Base
from app.core.encryption import encrypt_data, decrypt_data
import json

class EncryptedJSON(TypeDecorator):
    """
    Encrypts JSON data on the way in, decrypts on the way out.
    Stores as text in the DB.
    """
    impl = SQLString
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return encrypt_data(value)
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return decrypt_data(value)
        return None

class ConnectorConfig(Base):
    __tablename__ = "connector_configs"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    source_type = Column(String, nullable=False) # e.g. "github", "slack", "notion"
    config_data = Column(EncryptedJSON, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False)
