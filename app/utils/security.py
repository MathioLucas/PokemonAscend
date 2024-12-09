from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from app.models.Base import User
from app.schemas.user_schema import UserCreate, UserLogin

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "your-secret-key-replace-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class UserService:
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hashing the user's password
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verifying the provided password against the stored hash
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        """
        Createing a new user in the database
        """
        hashed_password = UserService.hash_password(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            trainer_level=1,
            total_battles=0,
            total_wins=0
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def authenticate_user(db: Session, login: UserLogin) -> User | None:
        """
        Authenticateing user and return user if credentials are valid
        """
        user = db.query(User).filter(User.username == login.username).first()
        if not user:
            return None
        if not UserService.verify_password(login.password, user.hashed_password):
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        return user

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None):
        """
        Createing a JWT access token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt