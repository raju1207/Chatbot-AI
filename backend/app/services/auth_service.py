# PostgreSQL authentication logic will be implemented here.

from datetime import (
    datetime,
    timedelta,
    timezone,
)

from uuid import uuid4

import bcrypt
import jwt

from fastapi import (
    Depends,
    HTTPException,
    status,
)

from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from jwt.exceptions import (
    InvalidTokenError,
)

from app.config import settings

from app.database import (
    users_collection,
)


security = HTTPBearer(
    auto_error=False
)


def hash_password(
    password: str,
) -> str:
    password_bytes = (
        password.encode("utf-8")
    )

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt(),
    )

    return hashed.decode(
        "utf-8"
    )


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return bcrypt.checkpw(
        plain_password.encode(
            "utf-8"
        ),
        hashed_password.encode(
            "utf-8"
        ),
    )


def create_access_token(
    user_id: str,
) -> str:
    expires_at = (
        datetime.now(
            timezone.utc
        )
        + timedelta(
            minutes=
                settings.JWT_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": user_id,
        "exp": expires_at,
        "iat": datetime.now(
            timezone.utc
        ),
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=
            settings.JWT_ALGORITHM,
    )


async def create_user(
    name: str,
    email: str,
    password: str,
):
    normalized_email = (
        email
        .strip()
        .lower()
    )

    existing_user = (
        await users_collection
        .find_one(
            {
                "email":
                    normalized_email
            }
        )
    )

    if existing_user:
        raise HTTPException(
            status_code=
                status.HTTP_409_CONFLICT,

            detail=
                "An account with this email already exists.",
        )

    user_id = str(
        uuid4()
    )

    user = {
        "user_id":
            user_id,

        "name":
            name.strip(),

        "email":
            normalized_email,

        "password_hash":
            hash_password(
                password
            ),

        "created_at":
            datetime.now(
                timezone.utc
            ),
    }

    await users_collection.insert_one(
        user
    )

    return user


async def authenticate_user(
    email: str,
    password: str,
):
    normalized_email = (
        email
        .strip()
        .lower()
    )

    user = (
        await users_collection
        .find_one(
            {
                "email":
                    normalized_email
            }
        )
    )

    if not user:
        return None

    if not verify_password(
        password,
        user["password_hash"],
    ):
        return None

    return user


async def get_current_user(
    credentials:
        HTTPAuthorizationCredentials
        | None
        = Depends(security),
):
    if credentials is None:
        raise HTTPException(
            status_code=
                status.HTTP_401_UNAUTHORIZED,

            detail=
                "Authentication required.",

            headers={
                "WWW-Authenticate":
                    "Bearer"
            },
        )

    token = (
        credentials.credentials
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[
                settings.JWT_ALGORITHM
            ],
        )

        user_id = payload.get(
            "sub"
        )

        if not user_id:
            raise HTTPException(
                status_code=
                    status.HTTP_401_UNAUTHORIZED,

                detail=
                    "Invalid authentication token.",
            )

    except InvalidTokenError:
        raise HTTPException(
            status_code=
                status.HTTP_401_UNAUTHORIZED,

            detail=
                "Invalid or expired authentication token.",

            headers={
                "WWW-Authenticate":
                    "Bearer"
            },
        )

    user = (
        await users_collection
        .find_one(
            {
                "user_id":
                    user_id
            }
        )
    )

    if not user:
        raise HTTPException(
            status_code=
                status.HTTP_401_UNAUTHORIZED,

            detail=
                "User account not found.",
        )

    return user