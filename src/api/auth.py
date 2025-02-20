from fastapi import APIRouter, Depends, HTTPException, status, Security, BackgroundTasks, Request
from sqlalchemy.orm import Session
from src.schemas.users import UserCreate, Token, User, UserLogin, RequestEmail, PasswordReset, TokenRefreshRequest
from src.services.auth import create_access_token, Hash, get_email_from_token, create_refresh_token, verify_refresh_token
from src.services.users import UserService
from src.database.db import get_db

from src.services.email import send_email, send_reset_password_email

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    Register a new user.

    Args:
        user_data: The user data including email and password.
        background_tasks: BackgroundTasks instance to send confirmation email.
        request: The incoming request instance.
        db: Database session.

    Returns:
        The newly created user object.
    """
    user_service = UserService(db)
    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Користувач з таким email вже існує")
    
    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)
    background_tasks.add_task(send_email, new_user.email, new_user.username, request.base_url)
    return new_user

@router.post("/login", response_model=Token)
async def login_user(body: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return access and refresh tokens.

    Args:
        body: User login data (email, password).
        db: Database session.

    Returns:
        A dictionary containing access and refresh tokens.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)
    if not user or not Hash().verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неправильний логін або пароль", headers={"WWW-Authenticate": "Bearer"})
    
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Електронна адреса не підтверджена")
    
    access_token = await create_access_token(data={"sub": user.email})
    refresh_token = await create_refresh_token(data={"sub": user.email})
    user.refresh_token = refresh_token
    db.commit()
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh-token", response_model=Token)
async def new_token(request: TokenRefreshRequest, db: Session = Depends(get_db)):
    """
    Generate a new access token using a refresh token.

    Args:
        request: Refresh token request.
        db: Database session.
    
    Returns:
        A dictionary containing a new access token.
    """
    user = await verify_refresh_token(request.refresh_token, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
    
    new_access_token = await create_access_token(data={"sub": user.email})
    return {"access_token": new_access_token, "refresh_token": request.refresh_token, "token_type": "bearer"}

@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Confirm a user's email address.

    Args:
        token: Email confirmation token.
        db: Database session.
    
    Returns:
        A success message if the email is confirmed.
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ваша електронна пошта вже підтверджена")
    await user_service.confirmed_email(email)
    return {"message": "Електронну пошту підтверджено"}

@router.post("/request_email")
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    Request email confirmation.

    Args:
        body: Request containing user email.
        background_tasks: BackgroundTasks instance to send confirmation email.
        request: The incoming request instance.
        db: Database session.
    
    Returns:
        A message indicating whether the email was sent.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)
    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Перевірте свою електронну пошту для підтвердження"}

@router.post("/reset_password")
async def reset_password(body: RequestEmail, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    Send password reset email.

    Args:
        body: Request containing user email.
        background_tasks: BackgroundTasks instance to send reset email.
        request: The incoming request instance.
        db: Database session.
    
    Returns:
        A message indicating whether the reset email was sent.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Користувача не знайдено")    
    
    background_tasks.add_task(send_reset_password_email, user.email, user.username, request.base_url)
    return {"message": "Перевірте вашу електронну пошту для скидання пароля"}

@router.post("/change_password")
async def change_password(body: PasswordReset, db: Session = Depends(get_db)):
    """
    Change user password.

    Args:
        body: Password reset data containing the token and new password.
        db: Database session.
    
    Returns:
        A message confirming the password change.
    """
    email = await get_email_from_token(body.token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Невірний або прострочений токен")
    
    user.hashed_password = Hash().get_password_hash(body.new_password)
    await db.commit()
    return {"message": "Пароль успішно змінено"}