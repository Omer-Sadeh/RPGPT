import os
import time
from typing import Dict
import jwt
import bcrypt
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from backend.Utility import CustomException
from tinydb import TinyDB, Query

JWT_SECRET = os.getenv('AUTH_SECRET')
JWT_ALGORITHM = "HS256"


def sign_jwt(user_id: str) -> str:
    """
    Sign a JWT token with the user_id as the payload.

    :param user_id: The user_id to be signed into the token.
    :return: The signed token.
    """
    payload = {
        "user_id": user_id,
        "generated": time.time()
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def decode_jwt(token: str) -> dict:
    """
    Decode a JWT token and return the payload.

    :param token: The token to be decoded.
    :return: The payload of the token.
    """
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        now = time.time()
        # check if now is less than 1 day from the token generation time
        if now - decoded_token["generated"] > 86400:
            raise jwt.ExpiredSignatureError
        return decoded_token
    except jwt.ExpiredSignatureError:
        return {}


class JWTBearer(HTTPBearer):
    """
    A custom Bearer token class that verifies the token using the sign_jwt function.
    """

    def __init__(self, auto_error: bool = True):
        """
        Initialize the JWTBearer class.

        :param auto_error: Whether to raise an error if the token is invalid or expired.
        """
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        """
        Verify the token and return the token if it is valid.

        :param request: The request object.
        :return: The token if it is valid.
        """
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        """
        Verify the token and return whether it is valid.

        :param jwtoken: The token to be verified.
        :return: Whether the token is valid.
        """
        isTokenValid: bool = False

        try:
            payload = decode_jwt(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True

        return isTokenValid


class UserSchema(BaseModel):
    """
    A Pydantic model for the user schema.
    Fields:
    - username: The username of the user.
    - password: The password of the user.
    """
    username: str = Field(...)
    password: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "username": "Abdulazeez Abdulazeez Adeshina",
                "password": "weakpassword"
            }
        }


class AuthDatabase:
    """
    A class that handles the authentication database.
    """
    # Initialize the TinyDB database and the 'users' table.
    users = TinyDB('./backend/authDB.json').table('users')

    def user_exists(self, username: str) -> bool:
        """
        Check if a user exists in the database.

        :param username: The username of the user.
        :return: Whether the user exists.
        """
        return bool(self.users.search(Query().username == username))

    def authenticate_user(self, user_data: UserSchema) -> str:
        """
        Authenticate a user. If the user exists and the password is correct, return a signed JWT token.

        :param user_data: The user data to be authenticated.
        :return: The signed JWT token.
        """
        user = self.users.get(Query().username == user_data.username)
        if user and bcrypt.checkpw(user_data.password.encode("utf-8"), user["password"].encode("utf-8")):
            return sign_jwt(user_data.username)
        raise CustomException("Invalid credentials.")

    def register_user(self, user_data: UserSchema) -> str:
        """
        Register a user.
        If the user does not exist, hash the password and add the user to the database.

        :param user_data: The user data to be registered.
        :return: The signed JWT token.
        """
        username = user_data.username
        if self.user_exists(username):
            raise CustomException("User already exists.")
        password = user_data.password

        if len(username.split()) > 1:
            raise CustomException("Username must not contain spaces.")
        if len(password) < 8:
            raise CustomException("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in password):
            raise CustomException("Password must contain at least one digit.")
        if not any(char.isupper() for char in password):
            raise CustomException("Password must contain at least one uppercase letter.")
        if not any(char.islower() for char in password):
            raise CustomException("Password must contain at least one lowercase letter.")
        if not any(char in "!@#$%^&*()-+" for char in password):
            raise CustomException("Password must contain at least one special character.")

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        new_user = UserSchema(username=username, password=hashed_password.decode("utf-8"))
        self.users.insert(new_user.dict())
        return sign_jwt(username)

    def decode_token(self, token: str) -> str:
        """
        Decode a JWT token and return the user_id.

        :param token: The token to be decoded.
        :return: The user_id.
        """
        decoded = decode_jwt(token)
        if decoded:
            username = decoded["user_id"]
            if self.user_exists(username):
                return username
        raise CustomException("Invalid or expired token.")
