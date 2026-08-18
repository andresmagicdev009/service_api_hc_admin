from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from passlib.context import CryptContext
from app.modules.user.model import User, Tenant, UserRoleEnum, TenantStatusEnum
from app.modules.user.schema import UserCreate, TenantCreate


PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    
    @staticmethod
    def create_tenant(db: Session, tenant_in: TenantCreate) -> Tenant:
        if db.query(Tenant).filter(Tenant.ruc == tenant_in.ruc).first():
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Ya existe un tenant registrado con este RUC."
            )
            
        new_tenant = Tenant(
            tenant_name = tenant_in.tenant_name,
            ruc = tenant_in.ruc,
            plan = tenant_in.plan or "PRO",
        )
        
        #Aqui se esta creando el tenant en la base de datos, pero no se esta haciendo commit, por lo que no se guardara hasta que se haga commit en otra parte del codigo.
        db.add(new_tenant)
        
        # Aqui deberia ir posiblemente la logica para crear un esquema del tenant creado en la base de datos del ERP
        db.commit()
        db.refresh(new_tenant)
        return new_tenant
    
    @staticmethod
    def create_user(db: Session, user_in: UserCreate) -> User:
        #1 Validar que el tenant_id se encuentre en estado activo 
        tenant = db.query(Tenant).filter(
            Tenant.id == user_in.tenant_id,
            Tenant.status == TenantStatusEnum.ACTIVE
        ).first()
        if not tenant:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "El tenant especificado no existe o no se encuentra activo."
            )
        # 2 Validar unicidad del email
        if db.query(User).filter(User.email == user_in.email).first():
            raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Ya existe un usuario registrado con este correo electrónico."
    )
    
        #3 Guardar el usuario 
        hashed_pwd = PWD_CONTEXT.hash(user_in.password)
        new_user = User(
            tenant_id = tenant.id,
            email = user_in.email,
            hashed_password = hashed_pwd,
            full_name=user_in.full_name,
            role = user_in.role
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    