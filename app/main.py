from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import engine, Base, get_db
from app.models.Base import User
from app.schemas.user_schema import UserCreate, UserResponse, UserLogin
from app.services.security import UserService
from app.utilties.ErrorHandling import CustomErrorMiddleware, setup_exception_handlers
from app.models import PokemonTeam, PokemonTeamResponse, PokemonTeamCreate 
from app.services import get_current_user

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Pokemon Trainer Dashboard",
    description="A cloud-simulated backend for managing Pokemon trainer data",
    version="0.1.0"
)

app.add_middleware(CustomErrorMiddleware)

setup_exception_handlers(app)


@app.post("/users/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new Pokemon trainer
    """
   
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Create new user
    db_user = UserService.create_user(db, user)
    return db_user

@app.post("/users/login")
def login_user(login: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a Pokemon trainer and generate access token
    """
    user = UserService.authenticate_user(db, login)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Generate access token
    access_token = UserService.create_access_token(
        data={"sub": user.username}
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer"
    }


@app.post("/teams/", response_model=PokemonTeamResponse)
def create_team(team: PokemonTeamCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Create a new Pokemon team
    """
    # Create the team associated with the current user
    db_team = PokemonTeam(name=team.name, trainer_id=current_user.id)
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    
    return db_team



@app.get("/users/me", response_model=UserResponse)
def read_users_me(db: Session = Depends(get_db)):
    """
    Get current user's profile
    Note: In a full implementation, this would use JWT token authentication
    """

    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
@app.get("/cause-error")
async def cause_error():
    raise ValueError("This is a test error!")

@app.get("/not-found")
async def not_found():
    raise HTTPException(status_code=404, detail="This route does not exist")