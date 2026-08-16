import enum

class SystemRole(str, enum.Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "Admin"
    CUSTOMER = "Customer"
    ENTERPRISE = "Enterprise"
    