from fastapi import Depends, HTTPException, status
from app.models.user import User
from app.services.auth import get_current_user

# Hierarquia: quanto maior, mais permissões
_ROLE_LEVEL = {"admin": 3, "manager": 2, "sales": 1}


def _require_role(minimum_role: str):
    """Factory que retorna uma dependency FastAPI exigindo nível mínimo de role."""
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        level = _ROLE_LEVEL.get(current_user.role or "sales", 1)
        if level < _ROLE_LEVEL[minimum_role]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Requer papel '{minimum_role}' ou superior.",
            )
        return current_user
    # Nomeia a função para o OpenAPI mostrar corretamente
    dependency.__name__ = f"require_{minimum_role}"
    return dependency


require_admin   = _require_role("admin")    # somente admin
require_manager = _require_role("manager")  # admin + manager
require_sales   = _require_role("sales")    # todos os papéis autenticados
