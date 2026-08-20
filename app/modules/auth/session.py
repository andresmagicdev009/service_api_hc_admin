from typing import Dict 


##
""" USAR REDIS AL REFACTORIZAR PARA GUARDAR LOS TOKENS ACTIVOS Y SU USUARIO ASOCIADO"""

##
# Estado en memoria para guardar token activos (Token -> Username) 
active_sessions: Dict[str, str] = {}  # Diccionario para almacenar sesiones activas