from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str = Field(default="viewer")

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class MasterDataCreate(BaseModel):
    data_set_name: str = Field(..., min_length=1, max_length=100)
    data_type: str = Field(..., min_length=1, max_length=50)
    data_value: str

class MasterDataUpdate(BaseModel):
    data_set_name: Optional[str] = None
    data_type: Optional[str] = None
    data_value: Optional[str] = None
    status: Optional[str] = None

class MasterDataResponse(BaseModel):
    id: int
    data_set_name: str
    data_type: str
    data_value: str
    status: str
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True

class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    action: str
    table_name: Optional[str]
    record_id: Optional[int]
    old_value: Optional[str]
    new_value: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class DataQualityReport(BaseModel):
    total_records: int
    valid_records: int
    invalid_records: int
    accuracy: float
    data_set_name: str
    validation_date: datetime