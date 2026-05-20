from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse, ProfileUpdate
from app.services.activity_service import log_activity
from app.services.auth import create_access_token, get_current_user, hash_password, verify_password
from app.services.workspace import create_workspace

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    workspace = create_workspace(db, data.name)
    user = User(
        name=data.name,
        email=data.email,
        hashed_password=hash_password(data.password),
        role="admin",
        is_admin=True,
        workspace_id=workspace.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
        )
    log_activity(
        db,
        workspace_id=user.workspace_id,
        type="user_login",
        description=f"{user.name} fez login",
        user_id=user.id,
        meta={"email": user.email},
    )
    return {"access_token": create_access_token(user.id), "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/profile", response_model=UserResponse)
def update_profile(
    data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.name is not None:
        if not data.name.strip():
            raise HTTPException(status_code=400, detail="Nome não pode ser vazio")
        current_user.name = data.name.strip()

    if data.new_password is not None:
        if not data.current_password:
            raise HTTPException(status_code=400, detail="Senha atual é obrigatória")
        if not verify_password(data.current_password, current_user.hashed_password):
            raise HTTPException(status_code=400, detail="Senha atual incorreta")
        if len(data.new_password) < 6:
            raise HTTPException(status_code=400, detail="Nova senha deve ter pelo menos 6 caracteres")
        current_user.hashed_password = hash_password(data.new_password)

    db.commit()
    db.refresh(current_user)
    return current_user
