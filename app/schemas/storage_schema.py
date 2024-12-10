from pydantic import BaseModel, Field
from typing import Dict, Any, List
from datetime import datetime
from uuid import UUID

class StorageMetadata(BaseModel):
    """
    Metadata for distributed storage entries
    """
    storage_id: str
    user_id: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    data_type: str
    total_size: int = 0

class StorageBackupEntry(BaseModel):
    """
    Represents a backup entry in distributed storage
    """
    backup_id: str
    original_storage_id: str
    backup_timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any]

class StorageRecoveryRequest(BaseModel):
    """
    Request model for storage recovery
    """
    storage_id: str
    recovery_type: str = Field(default='full', pattern='^(full|partial)$')
    specific_fields: List[str] = []