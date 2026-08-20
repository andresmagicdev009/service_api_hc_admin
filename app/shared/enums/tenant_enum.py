import enum 

class TenantStatusEnum(enum.Enum):
    ACTIVE = "ACTIVO"
    INACTIVE = "INACTIVO"
    SUSPENDED = "SUSPENDIDO"

class ServiceTypeEnum(str, enum.Enum):
    ERP = "ERP"
    CRM = "CRM"

class UserRoleEnum(str, enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    OPERATOR = "OPERATOR"
    CUSTOMER_TENANT = "CUSTOMER TENANT"