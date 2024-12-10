from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.storage.distributed_storage import DistributedTrainerStorageManager
from app.services.pokemon_storage_service import PokemonStorageService
from app.schemas import PokemonTeamCreate, PokemonTeamResponse
from services.security import get_current_user

router = APIRouter(prefix="/pokemon", tags=["pokemon"])

def get_pokemon_storage_service(
    db: Session = Depends(get_db),
    storage_manager: DistributedTrainerStorageManager = Depends()
):
    """
    Dependency to create PokemonStorageService
    """
    return PokemonStorageService(db, storage_manager)

@router.post("/team", response_model=PokemonTeamResponse)
async def create_pokemon_team(
    team_data: PokemonTeamCreate,
    current_user_id: int = Depends(get_current_user),  # Implement this dependency
    storage_service: PokemonStorageService = Depends(get_pokemon_storage_service)
):
    """
    Create a new Pokemon team with distributed storage
    """
    try:
        team = await storage_service.create_pokemon_team(
            user_id=current_user_id, 
            team_data=team_data
        )
        return team
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/team/{team_id}", response_model=PokemonTeamResponse)
async def retrieve_pokemon_team(
    team_id: int,
    current_user_id: int = Depends(get_current_user),
    storage_service: PokemonStorageService = Depends(get_pokemon_storage_service)
):
    """
    Retrieve a Pokemon team with distributed storage fallback
    """
    try:
        team = await storage_service.retrieve_pokemon_team(
            team_id=team_id, 
            user_id=current_user_id
        )
        return team
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/team/{team_id}/backup")
async def backup_pokemon_team(
    team_id: int,
    current_user_id: int = Depends(get_current_user),
    storage_service: PokemonStorageService = Depends(get_pokemon_storage_service)
):
    """
    Manually trigger backup of a Pokemon team
    """
    try:
        backup_id = await storage_service.backup_pokemon_team(
            team_id=team_id, 
            user_id=current_user_id
        )
        return {"backup_id": backup_id, "message": "Team backed up successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))