from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.connector import ConnectorRepository
from app.db.models.connector import ConnectorConfig
import uuid

class ConnectorService:
    def __init__(self, db: AsyncSession):
        self.repo = ConnectorRepository(db)

    async def list_connectors(self, user_id: uuid.UUID) -> List[ConnectorConfig]:
        return await self.repo.get_by_user(user_id)

    async def create_connector(self, name: str, source_type: str, config_data: Dict[str, Any], is_active: bool, user_id: uuid.UUID) -> ConnectorConfig:
        obj_in = {
            "id": str(uuid.uuid4()),
            "name": name,
            "source_type": source_type,
            "config_data": config_data,
            "is_active": is_active,
            "user_id": user_id
        }
        return await self.repo.create(obj_in)

    async def update_connector(self, connector_id: str, name: Optional[str], config_data: Optional[Dict[str, Any]], is_active: Optional[bool], user_id: uuid.UUID) -> ConnectorConfig | None:
        connector = await self.repo.get_by_id_and_user(connector_id, user_id)
        if not connector:
            return None
        
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if config_data is not None:
            update_data["config_data"] = config_data
        if is_active is not None:
            update_data["is_active"] = is_active
            
        if update_data:
            connector = await self.repo.update(connector, update_data)
        return connector

    async def delete_connector(self, connector_id: str, user_id: uuid.UUID) -> bool:
        connector = await self.repo.get_by_id_and_user(connector_id, user_id)
        if not connector:
            return False
            
        return await self.repo.delete(connector.id)
