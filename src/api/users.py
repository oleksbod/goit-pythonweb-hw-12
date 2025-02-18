from fastapi import APIRouter, Depends, Request, UploadFile, File
from src.schemas.users import User
from src.services.auth import get_current_user, get_current_moderator_user
from src.services.limiter import limiter
from src.services.upload_file import UploadFileService
from src.services.users import UserService
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.conf.config import settings


router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=User)
@limiter.limit("5/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    return user

@router.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_moderator_user),
    db: AsyncSession = Depends(get_db),
):
    avatar_url = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user
