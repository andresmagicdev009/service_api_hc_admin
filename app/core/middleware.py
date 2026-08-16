from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.context import client_ip_ctx

class ClientIPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        #1. Intentar obtener la IP detras de Proxies / load balancers 
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            #Tomar la primera IP de la lista si hay multiples proxys 
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            # Si no hay proxy, tomar la IP directa del cliente o header X-Real-IP
            ip = request.headers.get("X-Real-IP") or (
                request.client.host if request.client else "unknown"
            )
            
        #2. Guardar la IP en la variable de contexto 
        token = client_ip_ctx.set(ip)
        
        try: 
            response = await call_next(request)
            return response
        finally:
            # 3. Limpiar el contexto al finalizar la peticion 
            client_ip_ctx.reset(token)