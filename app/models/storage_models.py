from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base
from datetime import datetime

class StorageModel(Base):
    """
    SQLAlchemy model for storing storage metadata
    """
    __tablename__ = "storage_entries"

    id = Column(Integer, primary_key=True, index=True)
    storage_id = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    data_type = Column(String, nullable=False)
    total_size = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to backups
    backups = relationship("BackupModel", back_populates="original_storage")
    
    # Relationship to user
    user = relationship("User", back_populates="storage_entries")

class BackupModel(Base):
    """
    SQLAlchemy model for storing backup entries
    """
    __tablename__ = "storage_backups"

    id = Column(Integer, primary_key=True, index=True)
    backup_id = Column(String, unique=True, nullable=False, index=True)
    original_storage_id = Column(String, ForeignKey('storage_entries.storage_id'), nullable=False)
    backup_timestamp = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, nullable=True)  # Store additional backup metadata
    
    # Relationship back to original storage
    original_storage = relationship("StorageModel", back_populates="backups")

# Update User model to include relationship (add to your existing User model)
# User.storage_entries = relationship("StorageModel", back_populates="user")