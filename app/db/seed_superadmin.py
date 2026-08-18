import asyncio

from sqlalchemy import select
from app.db.data_connect import get_db_session
from app.modules.user.model import Tenant, User, TenantStatusEnum, UserRoleEnum
from app.modules.user.service import PWD_CONTEXT


async def run_seed():
    async for db in get_db_session():
        try:
            # 1. Crear o recuperar Tenant inicial con RUC de Ecuador (13 dígitos)
            result = await db.execute(
                select(Tenant).where(Tenant.ruc == "1790000000001")
            )
            tenant = result.scalar_one_or_none()

            if not tenant:
                tenant = Tenant(
                    tenant_name="Empresa Principal",
                    ruc="1790000000001",
                    plan="PRO",
                    status=TenantStatusEnum.ACTIVE,
                )
                db.add(tenant)
                await db.commit()
                await db.refresh(tenant)
                print(f"Tenant creado exitosamente (ID: {tenant.id})")

            # 2. Crear Super Admin
            email = "admin@facsys.com"
            admin_result = await db.execute(select(User).where(User.email == email))
            existing_admin = admin_result.scalar_one_or_none()

            if existing_admin:
                print(f"El usuario {email} ya existe.")
                return

            super_admin = User(
                tenant_id=tenant.id,
                email=email,
                hashed_password=PWD_CONTEXT.hash("Admin12345!"),
                full_name="Super Administrador",
                role=UserRoleEnum.SUPER_ADMIN,
                is_active=True,
            )
            db.add(super_admin)
            await db.commit()
            print(f"Usuario Super Admin creado asignado al tenant_id '{tenant.id}'")

        except Exception as e:
            await db.rollback()
            print(f"Error registrando el seed: {e}")


if __name__ == "__main__":
    asyncio.run(run_seed())