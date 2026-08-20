import re 
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

SCHEMAS_DDL = {
    "ERP": """
        CREATE TABLE IF NOT EXISTS {schema_name}.invoices (
            id SERIAL PRIMARY KEY,
            invoice_number VARCHAR(50) NOT NULL,
            total DECIMAL(10, 2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS {schema_name}.products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            price DECIMAL(10, 2) NOT NULL
        );
    """,
    "CRM": """
        CREATE TABLE IF NOT EXISTS {schema_name}.customers (
            id SERIAL PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL
        );
        CREATE TABLE IF NOT EXISTS {schema_name}.leads (
            id SERIAL PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            status VARCHAR(50) DEFAULT 'NEW'
        );
    """
}


async def create_tenant_schema(db: AsyncSession, schema_name: str, service_type: str):
    # Santiziar el esquema para evitar inyeccion SQL 
    clean_schema = re.sub(r'[^a-zA-Z0-9_]', '', schema_name)
    
    #1 Creal el esquema PostgreSQL
    await db.execute(text(f"CREATE SCHEMA IF NOT EXISTS {clean_schema};"))
    
    #2 Ejecutar las tablas base segun el tipo seleccionado (ERP?/CRM)
    ddl_script = SCHEMAS_DDL.get(service_type.upper())
    if not ddl_script:
        raise ValueError(f"Tipo de servicio desconocido: {service_type}")
    
    formatted_ddl = ddl_script.format(schema_name=clean_schema)
    await db.execute(text(formatted_ddl))
    await db.commit()
    