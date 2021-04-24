from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks

from app.utils.jwt import signJWT
from app.db.user import UserTableHandler
from app.utils.email import send_email
from app.core.users import get_current_user
from app.schemas.user import User, UserLogin, UserToken, BaseResponse, UserPasswordChange, UserInDB
from app.utils.hash import verify_code, verify_password
from app.core.config import ACCESS_TOKEN_EXPIRE_SECONDS, API_PREFIX, API_AUTH_PREFIX

router = APIRouter(prefix=API_AUTH_PREFIX)

@router.post("/register", response_model=BaseResponse)
async def register(request: Request, user: User, background_tasks: BackgroundTasks):
    """
        registers the new user and sends verification email in background
    """
    user_in_db = await UserTableHandler.find_by_email(user.email)
    if user_in_db:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_id, verification_code = await UserTableHandler.add(user)
    if user_id:
        await send_email([user.email], 
                        f"{request.base_url}{API_PREFIX[1:]}{API_AUTH_PREFIX}/verify?user_id={user_id}&code={verification_code}",
                        background_tasks)
        return {"success": True, "message": "The user has been created and a verification message has been sent"}
    else:
        raise HTTPException(status_code=400, detail="The user couldn't be created")

@router.post("/login", response_model=UserToken)
async def login(user: UserLogin):
    """
        Authenticates verified user and returns a jwt token
    """

    user_in_db = await UserTableHandler.find_by_email(user.email)
    if not user_in_db:
        raise HTTPException(status_code=400, detail="The user does not exist")

    if not user_in_db.get('is_verified'):
        raise HTTPException(status_code=400, detail="The user has not been verified yet")

    if not verify_password(user.password, user_in_db.get('password')):
        raise HTTPException(status_code=400, detail="Incorrect credentials")

    jwt_token = signJWT(user.email)
    if jwt_token:
        return {"success": True, "message": "The user has authenticated successfully", "token": jwt_token, "expires_in": ACCESS_TOKEN_EXPIRE_SECONDS}

    raise HTTPException(status_code=400, detail="Could not generate the access token")

@router.get("/verify", response_model=BaseResponse)
async def verify(user_id: int, code: str):
    """
        verifies the user based on the hashed code, updates the column and 
        removes the corresponding record from verifications table.
    """
    user = await UserTableHandler.find_by_id(user_id)
    if user:
        if user.get('is_verified', False):
            raise HTTPException(status_code=400, detail="User already verified")
        if verify_code(f"{user.get('fullname')}:{user.get('email')}", code):
            await UserTableHandler.verify_user(user_id, is_verified=True)
            return {"success": True, "message": "The user has been verified successfully"}
        else:
            raise HTTPException(status_code=400, detail="Invalid verification code")
    else:
        raise HTTPException(status_code=400, detail="User does not exist")

@router.post("/password", response_model=BaseResponse)
async def password( password_change: UserPasswordChange, current_user: UserInDB = Depends(get_current_user)):
    """
        updates the current user's password. The current user is taken from jwt token
    """
    if not current_user.is_verified:
        raise HTTPException(status_code=400, detail="User is not verified")
    
    await UserTableHandler.update_password(current_user.id, password_change.new_password)
    return {"success": True, "message": "The password has been changed successfully"}