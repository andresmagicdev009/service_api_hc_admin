from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional
from app.modules.user.model import UserRoleEnum, TenantStatusEnum

class TenantCreate(BaseModel):
    tenant_name: str
    ruc: str
    plan: Optional[str] = "PRO"

class TenantResponse(BaseModel):
    id: UUID 
    tenant_name: str
    ruc: str
    plan: str
    status: TenantStatusEnum
    
    class Config: 
        from_attributes = True
        
class UserCreate(BaseModel):
    tenant_id: UUID
    email: EmailStr
    password: str
    full_name: str
    role: Optional[UserRoleEnum] = UserRoleEnum.ADMIN
    
    
class UserResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    email: EmailStr
    full_name: str
    role: UserRoleEnum
    is_active: bool

    class Config:
        from_attributes = True