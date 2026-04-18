from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, List
from config.database import DatabaseConfig

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "mdm_system_secret_key_2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class RBACService:
    PERMISSIONS = {
        "admin": ["create", "read", "update", "delete", "manage_users", "view_audit"],
        "editor": ["create", "read", "update"],
        "viewer": ["read"]
    }

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def decode_access_token(token: str) -> Optional[dict]:
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            return None

    @staticmethod
    def has_permission(role: str, permission: str) -> bool:
        return permission in RBACService.PERMISSIONS.get(role, [])

    @staticmethod
    def get_user_permissions(role: str) -> List[str]:
        return RBACService.PERMISSIONS.get(role, [])

    @staticmethod
    def register_user(username: str, email: str, password: str, role: str = "viewer") -> int:
        password_hash = RBACService.hash_password(password)
        with DatabaseConfig.get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role)
                VALUES (?, ?, ?, ?)
            """, (username, email, password_hash, role))
            return cursor.lastrowid

    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[dict]:
        with DatabaseConfig.get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username = ? AND is_active = 1", (username,))
            row = cursor.fetchone()
            if row and RBACService.verify_password(password, row["password_hash"]):
                return dict(row)
            return None

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[dict]:
        with DatabaseConfig.get_db_cursor() as cursor:
            cursor.execute("SELECT id, username, email, role, is_active, created_at FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    @staticmethod
    def get_all_users() -> List[dict]:
        with DatabaseConfig.get_db_cursor() as cursor:
            cursor.execute("SELECT id, username, email, role, is_active, created_at FROM users")
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def update_user_role(user_id: int, new_role: str) -> bool:
        with DatabaseConfig.get_db_cursor(commit=True) as cursor:
            cursor.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
            return cursor.rowcount > 0

    @staticmethod
    def deactivate_user(user_id: int) -> bool:
        with DatabaseConfig.get_db_cursor(commit=True) as cursor:
            cursor.execute("UPDATE users SET is_active = 0 WHERE id = ?", (user_id,))
            return cursor.rowcount > 0