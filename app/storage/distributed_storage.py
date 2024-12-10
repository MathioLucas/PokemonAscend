import os
import json
import uuid
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import shutil

class DistributedTrainerStorageManager:
    """
    Advanced distributed storage manager simulating cloud-like storage
    """
    def __init__(
        self, 
        base_storage_path: str = './trainer_storage', 
        backup_path: str = './trainer_backups',
        max_backups: int = 5,
        shard_count: int = 3
    ):
        """
        Initialize storage manager
        
        :param base_storage_path: Primary storage location
        :param backup_path: Backup storage location
        :param max_backups: Maximum number of backups to retain
        :param shard_count: Number of virtual shards for data distribution
        """
        self.base_storage_path = base_storage_path
        self.backup_path = backup_path
        self.max_backups = max_backups
        self.shard_count = shard_count
        
        # Create storage directories
        os.makedirs(base_storage_path, exist_ok=True)
        os.makedirs(backup_path, exist_ok=True)
    
    def _get_shard_path(self, storage_id: str) -> str:
        """
        Determine shard path based on consistent hashing
        
        :param storage_id: Unique identifier for the storage entry
        :return: Shard path for storing/retrieving data
        """
        shard_index = hash(storage_id) % self.shard_count
        shard_path = os.path.join(self.base_storage_path, f'shard_{shard_index}')
        os.makedirs(shard_path, exist_ok=True)
        return shard_path
    
    async def save_trainer_data(self, data: Dict[str, Any]) -> str:
        """
        Save trainer data with distributed storage simulation
        
        :param data: Dictionary containing trainer information
        :return: Unique storage ID
        """
        # Ensure storage ID exists
        storage_id = data.get('storage_id', str(uuid.uuid4()))
        data['storage_id'] = storage_id
        data['last_updated'] = datetime.now().isoformat()
        
        # Select appropriate shard
        shard_path = self._get_shard_path(storage_id)
        file_path = os.path.join(shard_path, f'{storage_id}.json')
        
        # Simulate asynchronous write with a slight delay
        await asyncio.sleep(0.1)
        
        # Write data
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Create backup
        await self._create_backup(storage_id)
        
        return storage_id
    
    async def _create_backup(self, storage_id: str):
        """
        Create a timestamped backup of storage data
        
        :param storage_id: Unique identifier for the storage entry
        """
        shard_path = self._get_shard_path(storage_id)
        source_file = os.path.join(shard_path, f'{storage_id}.json')
        
        if not os.path.exists(source_file):
            return
        
        # Create backup directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(self.backup_path, storage_id)
        os.makedirs(backup_dir, exist_ok=True)
        
        backup_file = os.path.join(backup_dir, f'{storage_id}_backup_{timestamp}.json')
        shutil.copy2(source_file, backup_file)
        
        # Manage backup rotation
        await self._rotate_backups(storage_id)
    
    async def _rotate_backups(self, storage_id: str):
        """
        Rotate backups, keeping only the most recent backups
        
        :param storage_id: Unique identifier for the storage entry
        """
        backup_dir = os.path.join(self.backup_path, storage_id)
        
        # Get all backup files, sorted by modification time
        backup_files = sorted(
            [f for f in os.listdir(backup_dir) if f.endswith('.json')],
            key=lambda x: os.path.getmtime(os.path.join(backup_dir, x)),
            reverse=True
        )
        
        # Remove excess backups
        for backup_file in backup_files[self.max_backups:]:
            os.remove(os.path.join(backup_dir, backup_file))
    
    async def simulate_distributed_recovery(self, storage_id: str) -> Dict[str, Any]:
        """
        Simulate distributed data recovery with multiple fallback mechanisms
        
        :param storage_id: Unique identifier for the storage entry
        :return: Recovered storage data
        """
        # Primary retrieval from sharded storage
        shard_path = self._get_shard_path(storage_id)
        primary_file = os.path.join(shard_path, f'{storage_id}.json')
        
        # Try primary storage
        if os.path.exists(primary_file):
            with open(primary_file, 'r') as f:
                return json.load(f)
        
        # Backup retrieval
        backup_dir = os.path.join(self.backup_path, storage_id)
        
        if os.path.exists(backup_dir):
            backup_files = sorted(
                [f for f in os.listdir(backup_dir) if f.endswith('.json')],
                key=lambda x: os.path.getmtime(os.path.join(backup_dir, x)),
                reverse=True
            )
            
            if backup_files:
                latest_backup = os.path.join(backup_dir, backup_files[0])
                with open(latest_backup, 'r') as f:
                    return json.load(f)
        
        raise FileNotFoundError(f"No data found for storage ID {storage_id}")

class BackupManager:
    """
    Manager for handling backup-related operations
    """
    def __init__(self, storage_manager: DistributedTrainerStorageManager):
        """
        Initialize backup manager
        
        :param storage_manager: Distributed storage manager
        """
        self.storage_manager = storage_manager
    
    async def create_backup(self, storage_id: str) -> str:
        """
        Create a backup for a given storage entry
        
        :param storage_id: Unique identifier for the storage entry
        :return: Backup file path
        """
        try:
            # Retrieve original data
            original_data = await self.storage_manager.simulate_distributed_recovery(storage_id)
            
            # Generate backup ID
            backup_id = str(uuid.uuid4())
            original_data['backup_id'] = backup_id
            
            # Save backup
            backup_storage_id = await self.storage_manager.save_trainer_data(original_data)
            
            return backup_storage_id
        except Exception as e:
            raise RuntimeError(f"Failed to create backup: {str(e)}")
    
    async def retrieve_backup(self, backup_id: str) -> Dict[str, Any]:
        """
        Retrieve a backup by its ID
        
        :param backup_id: Unique identifier for the backup
        :return: Backup data
        """
        try:
            return await self.storage_manager.simulate_distributed_recovery(backup_id)
        except FileNotFoundError:
            raise ValueError(f"Backup not found for ID: {backup_id}")