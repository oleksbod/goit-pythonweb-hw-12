from fastapi import APIRouter, Depends, Request, UploadFile, File
from src.schemas.users import User
from src.services.auth import get_current_user, get_current_admin_user
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
    """
    Retrieve the currently authenticated user's information.

    This endpoint returns the user data of the currently authenticated user.

    **Rate Limiting**:
    - This endpoint is limited to 5 requests per minute.

    Args:
        request (Request): The HTTP request object.
        user (User): The current authenticated user, retrieved through the `get_current_user` dependency.

    Returns:
        User: The authenticated user's information.
    """
    return user

@router.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update the avatar of the current user.

    This endpoint allows the current authenticated admin user to upload and update the avatar
    of the user. The avatar image will be uploaded to the cloud, and the user's record will
    be updated with the new avatar URL.

    Args:
        file (UploadFile): The avatar image file to upload.
        user (User): The authenticated admin user, retrieved through the `get_current_admin_user` dependency.
        db (AsyncSession): The database session, injected by the `get_db` dependency.

    Returns:
        User: The user object with the updated avatar URL.
    
    Raises:
        HTTPException: If the file upload or user update fails.
    """
    avatar_url = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user
