# src/routes/auth_routes.py - VERSÃO CORRIGIDA

import json
import uuid
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from qodo.auth.auth_jwt import (
    create_access_token,
    create_refresh_token,
    verify_password,
)
from qodo.auth.deps import reuseable_oauth
from qodo.core.cache import client
from qodo.logs.infos import LOGGER
from qodo.model.user import Usuario


# Schema para a resposta de login compatível com o frontend
class LoginResponse(BaseModel):
    id: int
    username: str
    email: str
    empresa: str
    empresa_id: int
    tipo: str
    message: str
    access_token: str
    refresh_token: str
    token_type: str
    session_id: str


class Login:
    def __init__(self):
        self.loginRT = APIRouter(
            tags=['Autenticação'],
        )
        self._register_routes()

    def _register_routes(self):
        # --- Rota /login CORRIGIDA ---
        @self.loginRT.post(
            '/login',
            response_model=LoginResponse,  # Usando nosso schema customizado
            status_code=status.HTTP_200_OK,
        )
        async def login(user: OAuth2PasswordRequestForm = Depends()):
            LOGGER.info(f'🔐 Tentativa de login: {user.username}')

            # 1. Autenticação
            db_user = await Usuario.get_or_none(email=user.username)
            if not db_user:
                LOGGER.warning(f'Usuário não encontrado: {user.username}')
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Credenciais inválidas',
                )

            if not verify_password(user.password, db_user.password):
                LOGGER.warning(f'Senha incorreta para: {user.username}')
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Credenciais inválidas',
                )

            # 2. Gerar Tokens
            user_id_str = str(db_user.id)
            access_token = create_access_token(user_id_str)
            refresh_token = create_refresh_token(user_id_str)

            # 3. Preparar Dados para Cache
            session_data_for_cache = {
                'id': db_user.id,
                'username': db_user.username,
                'email': db_user.email,
                'company_name': db_user.company_name,
                'cnpj': db_user.cnpj,
                'cpf': db_user.cpf,
                'is_active': db_user.is_active,
                'empresa_id': db_user.id,
                'tipo': 'admin',
            }

            # 4. Salvar no Redis (com expiração opcional)
            cache_key = f'token:{access_token}'
            await client.set(
                cache_key,
                json.dumps(session_data_for_cache, default=str),
                ex=86400,
            )  # Expira em 24 horas (opcional)
            LOGGER.info(f'Token salvo no cache. Chave: {cache_key}')

            # 5. Retorno FINAL - COMPATÍVEL com o frontend
            return LoginResponse(
                id=db_user.id,
                username=db_user.username,
                email=db_user.email,
                empresa=db_user.company_name,
                empresa_id=db_user.id,
                tipo='admin',
                message='Login realizado com sucesso',
                access_token=access_token,
                refresh_token=refresh_token,
                token_type='bearer',
                session_id=str(uuid.uuid4()),
            )

        # --- Rota /logout CORRIGIDA ---
        @self.loginRT.post('/logout')
        async def logout(token: str = Depends(reuseable_oauth)):
            """Encerra a sessão no Redis"""
            cache_key = f'token:{token}'

            # Verifica se o token existe antes de deletar
            exists = await client.exists(cache_key)
            if exists:
                await client.delete(cache_key)
                LOGGER.info(
                    f'Logout bem-sucedido. Chave removida: {cache_key}'
                )
                return {
                    'status': 200,
                    'message': 'Logout realizado com sucesso',
                }
            else:
                LOGGER.info(f'Token não encontrado no cache: {cache_key}')
                return {'status': 200, 'message': 'Sessão já encerrada'}

        # --- Nova rota para verificar usuário atual ---
        @self.loginRT.get('/me')
        async def get_current_user_info(token: str = Depends(reuseable_oauth)):
            """Retorna informações do usuário atual"""
            cache_key = f'token:{token}'
            user_data = await client.get(cache_key)

            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Token inválido ou expirado',
                )

            user_info = json.loads(user_data)
            return {
                'id': user_info.get('id'),
                'username': user_info.get('username'),
                'email': user_info.get('email'),
                'empresa': user_info.get('company_name'),
                'tipo': user_info.get('tipo'),
            }

        # --- Rotas auxiliares ---
        @self.loginRT.post('/refresh-session')
        async def refresh_session(request: Request):
            """Renova o tempo da sessão"""
            # Implemente conforme necessário
            return {'message': 'Sessão renovada com sucesso'}

        @self.loginRT.get('/debug-sessions')
        async def debug_sessions():
            """Endpoint para debug"""
            # Implementação simplificada
            return {'total_sessions': 0, 'sessions': {}}
