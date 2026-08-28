# Authentication routes will be implemented here.

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.models.user import (
    AuthResponse,
    LoginRequest,
    LogoutResponse,
    RegisterRequest,
    UserResponse,
)

from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    create_user,
    get_current_user,
)


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


def build_user_response(
    user: dict,
) -> UserResponse:
    return UserResponse(
        user_id=
            user["user_id"],

        name=
            user["name"],

        email=
            user["email"],
    )


@router.post(
    "/register",
    response_model=AuthResponse,
)
async def register(
    request: RegisterRequest,
):
    user = await create_user(
        name=request.name,
        email=str(
            request.email
        ),
        password=
            request.password,
    )

    token = (
        create_access_token(
            user["user_id"]
        )
    )

    return AuthResponse(
        access_token=token,

        user=
            build_user_response(
                user
            ),
    )


@router.post(
    "/login",
    response_model=AuthResponse,
)
async def login(
    request: LoginRequest,
):
    user = (
        await authenticate_user(
            email=str(
                request.email
            ),

            password=
                request.password,
        )
    )

    if not user:
        raise HTTPException(
            status_code=
                status.HTTP_401_UNAUTHORIZED,

            detail=
                "Invalid email or password.",
        )

    token = (
        create_access_token(
            user["user_id"]
        )
    )

    return AuthResponse(
        access_token=token,

        user=
            build_user_response(
                user
            ),
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
async def me(
    current_user=
        Depends(
            get_current_user
        ),
):
    return build_user_response(
        current_user
    )


@router.post(
    "/logout",
    response_model=LogoutResponse,
)
async def logout(
    current_user=
        Depends(
            get_current_user
        ),
):
    return LogoutResponse(
        message=
            "Logged out successfully."
    )