import logging
from fastapi import Depends, Request
from jose import JWTError, ExpiredSignatureError

logger = logging.getLogger(__name__)
from app.exceptions.auth import TokenMissingError, InvalidTokenError, UserNotFoundError, NotEnoughPrivilegesError
from app.api.dependencies.core import get_user_repository
from app.repositories.users import UserRepository
from app.core.security import decode_token
from app.models.user import User

def get_current_user(
    request: Request,
    user_repo: UserRepository = Depends(get_user_repository)
) -> User:
    token = request.cookies.get("access_token")
    if not token or not token.startswith("Bearer "):
        raise TokenMissingError()
    
    token = token.split(" ")[1]
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise InvalidTokenError(detail="Invalid token type")
        user_id = int(payload.get("sub"))
    except ExpiredSignatureError:
        logger.debug("Expired token received")
        raise InvalidTokenError(detail="Token has expired.")
    except (JWTError, ValueError, TypeError) as e:
        logger.debug(f"Invalid token: {e}")
        raise InvalidTokenError(detail="Invalid token.")
        
    user = user_repo.get_by_id(user_id)
    if not user:
        raise UserNotFoundError()
        
    return user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise NotEnoughPrivilegesError()
    return current_user
