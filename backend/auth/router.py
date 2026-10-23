from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.db.models.core.user import User, UserRole
from backend.db.models.core.farmer_profile import FarmerProfile
from backend.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse
from backend.schemas.farmer import FarmerProfileResponse
from backend.auth.jwt_handler import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse)
def register_farmer(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    # Check if username or phone already exists
    existing_user = db.query(User).filter((User.username == payload.username) | (User.phone == payload.phone)).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or phone already registered")

    # Create User
    new_user = User(
        username=payload.username,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        role=UserRole.FARMER,
        created_at=datetime.utcnow(),
    )
    db.add(new_user)
    db.flush()

    # Create FarmerProfile
    new_profile = FarmerProfile(
        user_id=new_user.id,
        full_name=payload.full_name,
        village=payload.village,
        taluk=payload.taluk or payload.village,
        district=payload.district,
        state=payload.state,
        preferred_mandi=payload.preferred_mandi,
        preferred_language=payload.preferred_language,
    )
    db.add(new_profile)
    db.commit()

    token = create_access_token(data={"sub": new_user.id, "role": new_user.role.value})
    return TokenResponse(
        access_token=token,
        user_id=new_user.id,
        username=new_user.username,
        role=new_user.role
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLoginRequest, db: Session = Depends(get_db)):
    if payload.username == "farmer_demo":
        user = db.query(User).filter(User.username.in_(["farmer_demo", "farmer"])).first()
    else:
        user = db.query(User).filter(User.username == payload.username).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    token = create_access_token(data={"sub": user.id, "role": user.role.value})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        username=user.username,
        role=user.role
    )


@router.get("/me", response_model=FarmerProfileResponse)
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(FarmerProfile).filter(FarmerProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Farmer profile not found")
    return profile
