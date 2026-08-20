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
    is_active: bool

    class Config:
        from_attributes = True

"""______
               .-"      "-.
              /            \
             |              |
             |,  .-.  .-.  ,|
             | )(__/  \__)( |
             |/     /\     \|
             (_     ^^     _)
              \__|IIIIII|__/
               | \IIIIII/ |
                \        /
                 `------'

"""
#Possible escalation of privileges | Possible mitigation to study
# Only an admin can change a role
class AdminUserUpdate(BaseModel):
    full_name: Optional[str]
    email: Optional[EmailStr]
    role: Optional[UserRoleEnum]
    is_active: Optional[bool]


# Por seguridad los usuarios normales no pueden cambiar el rol ni el estado de activación de otros usuarios, solo pueden cambiar su nombre y correo electrónico.
class UserUpdate(BaseModel):
    full_name: Optional[str]
    email: Optional[EmailStr]
    is_active: Optional[bool]
    
    