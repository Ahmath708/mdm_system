from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List
from services.auth_service import RBACService
from models.schemas import UserCreate, UserLogin, UserResponse, AuditLogResponse
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = RBACService.decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user = RBACService.get_user_by_id(payload.get("user_id"))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def require_permission(permission: str):
    def check(user = Depends(get_current_user)):
        if not RBACService.has_permission(user["role"], permission):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return check

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    try:
        user_id = RBACService.register_user(
            user_data.username,
            user_data.email,
            user_data.password,
            user_data.role
        )
        user = RBACService.get_user_by_id(user_id)
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = RBACService.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = RBACService.create_access_token(
        data={"user_id": user["id"], "role": user["role"]}
    )
    return {"access_token": access_token, "token_type": "bearer", "role": user["role"]}

@router.get("/me", response_model=UserResponse)
async def get_me(user = Depends(get_current_user)):
    return user

@router.get("/permissions")
async def get_permissions(user = Depends(get_current_user)):
    return {"permissions": RBACService.get_user_permissions(user["role"])}

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(user = Depends(require_permission("manage_users"))):
    return RBACService.get_all_users()

@router.put("/users/{user_id}/role")
async def update_user_role(user_id: int, new_role: str, user = Depends(require_permission("manage_users"))):
    success = RBACService.update_user_role(user_id, new_role)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Role updated successfully"}

@router.delete("/users/{user_id}")
async def deactivate_user(user_id: int, user = Depends(require_permission("manage_users"))):
    success = RBACService.deactivate_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deactivated"}