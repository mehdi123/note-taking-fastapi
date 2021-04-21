from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.schemas.user import UserInDB, UserPayload
from app.db.user import UserTableHandler
from app.utils.jwt import decodeJWT

class JWTBearerPayload(HTTPBearer):
    """
        Extract the HTTP bearer token and decode it
    """
    def __init__(self, auto_error: bool = True):
        super(JWTBearerPayload, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearerPayload, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            payload = await self.get_payload(credentials.credentials)
            if not payload:
                raise HTTPException(status_code=401, detail="Invalid token or expired token.")
            return payload
        else:
            raise HTTPException(status_code=401, detail="Invalid authorization code.")

    async def get_payload(self, jwtoken: str) -> dict:
        try:
            payload = decodeJWT(jwtoken)
        except:
            payload = None
        return payload

async def get_current_user(payload: UserPayload = Depends(JWTBearerPayload())) -> UserInDB:
    """
        Extract the user based on HTTP bearer jwt token
    """
    user_email = payload.get('user_email')
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_in_db = await UserTableHandler.find_by_email(user_email)
    if user_in_db:
        return UserInDB(**user_in_db)
    raise HTTPException(status_code=401, detail="Invalid authorization code.")
