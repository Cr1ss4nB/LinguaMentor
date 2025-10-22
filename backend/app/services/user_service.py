from typing import List, Optional
from beanie import PydanticObjectId
from app.models.user_model import User, UserCreate, UserResponse
from passlib.context import CryptContext
import logging


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

logger = logging.getLogger(__name__)


class UserService:
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using Argon2
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    async def create_user(user_data: UserCreate) -> UserResponse:
        """
        Create a new user in the database
        """
        try:

            existing_user = await User.find_one(User.email == user_data.email)
            if existing_user:
                raise ValueError("User with this email already exists")

            existing_username = await User.find_one(User.username == user_data.username)
            if existing_username:
                raise ValueError("Username already taken")


            if len(user_data.password) < 8:
                raise ValueError("Password must be at least 8 characters long")

   
            hashed_password = UserService.hash_password(user_data.password)

   
            user = User(
                email=user_data.email,
                username=user_data.username,
                full_name=user_data.full_name,
                hashed_password=hashed_password,
                language_preferences=user_data.language_preferences
            )


            await user.insert()

            logger.info(f"User created successfully: {user.email}")


            return UserResponse(
                _id=str(user.id),
                email=user.email,
                username=user.username,
                full_name=user.full_name,
                language_preferences=user.language_preferences,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at,
                updated_at=user.updated_at
            )

        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise

    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[UserResponse]:
        """
        Get user by ID
        """
        try:
            user = await User.get(PydanticObjectId(user_id))
            if user:
                return UserResponse(
                    _id=str(user.id),
                    email=user.email,
                    username=user.username,
                    full_name=user.full_name,
                    language_preferences=user.language_preferences,
                    is_active=user.is_active,
                    is_verified=user.is_verified,
                    created_at=user.created_at,
                    updated_at=user.updated_at
                )
            return None
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {str(e)}")
            raise

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        """
        Get user by email
        """
        try:
            return await User.find_one(User.email == email)
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {str(e)}")
            raise

    @staticmethod
    async def get_all_users(skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """
        Get all users with pagination
        """
        try:
            users = await User.find_all().skip(skip).limit(limit).to_list()
            return [
                UserResponse(
                    _id=str(user.id),
                    email=user.email,
                    username=user.username,
                    full_name=user.full_name,
                    language_preferences=user.language_preferences,
                    is_active=user.is_active,
                    is_verified=user.is_verified,
                    created_at=user.created_at,
                    updated_at=user.updated_at
                )
                for user in users
            ]
        except Exception as e:
            logger.error(f"Error getting all users: {str(e)}")
            raise

    @staticmethod
    async def delete_user(user_id: str) -> bool:
        """
        Delete a user by ID
        """
        try:
            user = await User.get(PydanticObjectId(user_id))
            if user:
                await user.delete()
                logger.info(f"User deleted: {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            raise


# Global service instance
user_service = UserService()