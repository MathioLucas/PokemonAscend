from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from app.models.Base import User
from app.schemas.user_schema import UserCreate, UserResponse, UserLogin
from app.services.security import UserService
from app.utilties.ErrorHandling import CustomErrorMiddleware, setup_exception_handlers
from app.models import PokemonTeam, PokemonTeamResponse, PokemonTeamCreate
from app.services import get_current_user
from app.services.battle_services import PokemonBattleService
from app.services.tournament_service import TournamentType, AdvancedTournamentService
from app.services.pokemon_storage_service import PokemonStorageService
from app.storage.distributed_storage import DistributedTrainerStorageManager
from typing import List

Base.metadata.create_all(bind=engine)

app = FastAPI(...)


app = FastAPI(
    title="Pokemon Trainer Dashboard",
    description="A cloud-simulated backend for managing Pokemon trainer data",
    version="0.1.0"
)

app.add_middleware(CustomErrorMiddleware)
setup_exception_handlers(app)

# Dependencies
def get_pokemon_storage_service(
    db: Session = Depends(get_db),
    storage_manager: DistributedTrainerStorageManager = Depends()
):
    return PokemonStorageService(db, storage_manager)

@app.post("/users/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )

    db_user = UserService.create_user(db, user)
    return db_user

@app.post("/users/login")
def login_user(login: UserLogin, db: Session = Depends(get_db)):
    user = UserService.authenticate_user(db, login)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    access_token = UserService.create_access_token(
        data={"sub": user.username}
    )

    return {
        "access_token": access_token, 
        "token_type": "bearer"
    }

@app.post("/teams/", response_model=PokemonTeamResponse)
def create_team(team: PokemonTeamCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_team = PokemonTeam(name=team.name, trainer_id=current_user.id)
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team

@app.get("/users/me", response_model=UserResponse)
def read_users_me(db: Session = Depends(get_db)):
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/pokemon/battle")
def simulate_battle(
    pokemon1_id: int, 
    pokemon2_id: int,
    db: Session = Depends(get_db),
    storage_service: PokemonStorageService = Depends(get_pokemon_storage_service)
):
    try:
        pokemon1 = storage_service.retrieve_pokemon_by_id(pokemon1_id)
        pokemon2 = storage_service.retrieve_pokemon_by_id(pokemon2_id)
        
        battle_outcome = PokemonBattleService.simulate_battle(pokemon1, pokemon2)
        return {
            "winner": battle_outcome.winner.name,
            "loser": battle_outcome.loser.name,
            "rounds": battle_outcome.rounds,
            "damage_dealt": battle_outcome.damage_dealt
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/pokemon/tournament")
async def simulate_pokemon_tournament(
    team_ids: List[int],
    tournament_type: TournamentType = TournamentType.SINGLE_ELIMINATION,
    current_user_id: int = Depends(get_current_user),
    storage_service: PokemonStorageService = Depends(get_pokemon_storage_service)
):
    try:
        tournament_teams = []
        for team_id in team_ids:
            team = await storage_service.retrieve_pokemon_team(
                team_id=team_id, 
                user_id=current_user_id
            )
            tournament_teams.append(team.pokemons)

        tournament_bracket = AdvancedTournamentService.create_tournament_bracket(
            tournament_teams,
            tournament_type
        )

        completed_tournament = AdvancedTournamentService.simulate_tournament(
            tournament_bracket
        )

        return {
            "tournament_type": completed_tournament.tournament_type.value,
            "champion": completed_tournament.champion.name,
            "total_rounds": completed_tournament.current_round,
            "matches": [
                {
                    "round": match.round_number,
                    "participants": [p.name for p in match.participants],
                    "winner": match.winner.name,
                    "loser": match.loser.name,
                    "match_details": match.match_details
                } for match in completed_tournament.matches
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
