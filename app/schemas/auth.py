from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr

    username: str = Field(
        min_length=3,
        max_length=20,
    )

    password: str = Field(
        min_length=8,
    )

    display_name: str | None = Field(
        default=None,
        max_length=100,
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        if not value.replace("_", "").isalnum():
            raise ValueError(
                "Username can contain only letters, numbers and underscore"
            )

        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not any(char.isupper() for char in value):
            raise ValueError(
                "Password must contain at least one uppercase letter"
            )

        if not any(char.islower() for char in value):
            raise ValueError(
                "Password must contain at least one lowercase letter"
            )

        if not any(char.isdigit() for char in value):
            raise ValueError(
                "Password must contain at least one digit"
            )

        if not any(not char.isalnum() for char in value):
            raise ValueError(
                "Password must contain at least one special character"
            )

        return value


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    username: str
    display_name: str | None
    role: str
    is_verified: bool
    is_active: bool