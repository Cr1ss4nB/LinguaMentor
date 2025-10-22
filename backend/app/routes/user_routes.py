from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.user_model import UserCreate, UserResponse
from app.services.user_service import user_service

router = APIRouter()


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Create a new user with email, username, password, and language preferences"
)
async def create_user(user_data: UserCreate):
    """
    Create a new user account.

    - **email**: User's email address (must be unique)
    - **username**: Unique username (3-50 characters)
    - **full_name**: User's full name
    - **password**: Password (min 8 characters)
    - **language_preferences**: List of languages user wants to learn
    """
    try:
        user = await user_service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )


@router.get(
    "/",
    response_model=List[UserResponse],
    summary="Get all users",
    description="Retrieve all users with pagination"
)
async def get_all_users(skip: int = 0, limit: int = 100):
    """
    Get all users with pagination.

    - **skip**: Number of users to skip (for pagination)
    - **limit**: Maximum number of users to return (default: 100)
    """
    try:
        users = await user_service.get_all_users(skip=skip, limit=limit)
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving users: {str(e)}"
        )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Retrieve a specific user by their ID"
)
async def get_user_by_id(user_id: str):
    """
    Get user by ID.

    - **user_id**: The unique identifier of the user
    """
    try:
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user: {str(e)}"
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete user by ID",
    description="Delete a specific user by their ID"
)
async def delete_user(user_id: str):
    """
    Delete user by ID.

    - **user_id**: The unique identifier of the user to delete
    """
    try:
        success = await user_service.delete_user(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return {"message": "User deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}"
        )