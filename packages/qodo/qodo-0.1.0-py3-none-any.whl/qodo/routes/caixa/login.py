import json
from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import (  # Necessário para comparação de datetime consciente de fuso horário
    ZoneInfo,
)

import bcrypt
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from pydantic import BaseModel, EmailStr

from qodo.auth.auth_jwt import (
    create_access_token,
    create_refresh_token,
    verify_password,
    verify_token,
)
from qodo.auth.deps_employes import (
    SystemEmployees,
    get_current_employee,
    reuseable_oauth,
)
from qodo.controllers.caixa.cash_controller import CashController
from qodo.core.cache import client  # Cliente Redis
from qodo.logs.infos import LOGGER
from qodo.model.caixa import Caixa
from qodo.model.employee import Employees
from qodo.model.user import Usuario
from qodo.schemas.login.form_login_checkout import (
    CustomOAuth2PasswordRequestForm,
)


# -------------------------------------------------------------
# SCHEMAS (MANTIDOS)
# -------------------------------------------------------------
class TokenCaixaSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    empresa: Optional[str] = None
    empresa_id: Optional[int] = None
    tipo: str
    message: str
    access_token: str
    refresh_token: str
    token_type: str
    value: float
    caixa_id: int
    caixa_status: str


class ValidateTokenResponse(BaseModel):
    valid: bool
    user_id: int
    username: str
    empresa: str
    empresa_id: int
    caixa_aberto: bool
    caixa_id: Optional[int]
    saldo_inicial: Optional[float]
    message: str


# -------------------------------------------------------------
# CLASSE PRINCIPAL
# -------------------------------------------------------------
class LoginCheckout:
    """Contém as rotas de login/abertura de caixa e gerenciamento de sessão."""

    def __init__(self):
        self.router = APIRouter()
        self._register_routes()

    def _register_routes(self):

        # --- ROTA: /open (Login e Abertura de Caixa) ---
        @self.router.post(
            '/open',
            status_code=status.HTTP_200_OK,
            response_model=TokenCaixaSchema,
        )
        async def login_and_open(
            user: CustomOAuth2PasswordRequestForm = Depends(),
        ):
            """
            Login para funcionários com verificação de credenciais e abertura de caixa.

            Args:
                user: Formulário customizado com username, password e valor_inicial

            Returns:
                TokenCaixaSchema: Dados do usuário, tokens e status do caixa

            Raises:
                HTTPException: 403 para admins, 401 credenciais inválidas, 500 erro interno
            """
            LOGGER.info(f'🔐 Tentativa de login: {user.username}')

            # 1. VALIDAÇÃO DE USUÁRIO E EMPRESA
            is_admin = await Usuario.get_or_none(email=user.username)
            if is_admin:
                LOGGER.warning(
                    f'❌ Tentativa de login como admin: {user.username}'
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='Administradores não podem abrir um caixa.',
                )

            # Busca funcionário com relacionamento de usuário (empresa)
            employee = await Employees.get_or_none(
                email=user.username
            ).select_related('usuario')

            # 🔍 DIAGNÓSTICO DETALHADO - Verifica o que está acontecendo
            if not employee:
                LOGGER.warning(f'❌ Email não encontrado: {user.username}')
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Credenciais inválidas.',
                )

            # Validação unificada: credenciais inválidas
            if not verify_password(user.password, employee.senha):
                # 🔍 TENTATIVA ALTERNATIVA DE VERIFICAÇÃO
                try:
                    # Verifica se a senha está em texto puro (para desenvolvimento)
                    if user.password == employee.senha:
                        LOGGER.warning(
                            '⚠️  Senha em texto puro detectada - considere hash BCrypt'
                        )
                        # Se funcionar com texto puro, continue (APENAS PARA DEV)
                        pass
                    else:
                        LOGGER.warning(
                            f'❌ Senha não confere para: {user.username}'
                        )
                        LOGGER.warning(f'🔍 Hash esperado: {employee.senha}')
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Credenciais inválidas.',
                        )
                except Exception as e:
                    LOGGER.error(f'❌ Erro na verificação de senha: {e}')
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail='Credenciais inválidas.',
                    )

            # Validação de status do funcionário
            if not employee.ativo or not employee.usuario:
                detail = (
                    'Funcionário inativo.'
                    if not employee.ativo
                    else 'Funcionário não vinculado a uma empresa.'
                )
                LOGGER.warning(
                    f'❌ Funcionário com problema de status: {user.username} - {detail}'
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail=detail
                )

            # Dados básicos para uso posterior
            company_id = employee.usuario_id
            employee_name = employee.nome
            company_name = employee.usuario.company_name

            LOGGER.info(
                f'✅ Credenciais válidas para {employee_name} - Empresa: {company_name}'
            )

            # 2. VERIFICAÇÃO E ABERTURA DE CAIXA
            caixa_status = 'novo'
            try:
                # O CashController verifica se já existe caixa aberto e retorna o objeto.
                caixa = await CashController.abrir_caixa(
                    funcionario_id=employee.id,
                    saldo_inicial=float(user.valor_inicial),
                    nome=employee_name,
                    company_id=company_id,
                )

                # CORREÇÃO CRÍTICA: Comparação de datetimes com tratamento de timezone
                # O caixa.criado_em é offset-aware (America/Sao_Paulo). Precisamos comparar corretamente.
                if caixa.criado_em.tzinfo is not None:
                    # Se caixa.criado_em é aware, convertemos agora para o mesmo timezone
                    agora = datetime.now(ZoneInfo('America/Sao_Paulo'))
                    criado_em_aware = caixa.criado_em
                else:
                    # Se caixa.criado_em é naive, usamos datetime.now() sem timezone
                    agora = datetime.now()
                    criado_em_aware = caixa.criado_em.replace(tzinfo=None)

                # Determina se o caixa foi aberto agora ou já estava aberto
                if criado_em_aware < (agora - timedelta(seconds=5)):
                    caixa_status = 'ja_aberto'
                    message = 'Login realizado - Caixa já estava aberto.'
                    LOGGER.info(
                        f'ℹ️  Caixa já estava aberto para {employee_name}: ID {caixa.caixa_id}'
                    )
                else:
                    caixa_status = 'novo'
                    message = 'Login e Caixa abertos com sucesso.'
                    LOGGER.info(
                        f'✅ Novo caixa aberto para {employee_name}: ID {caixa.caixa_id}'
                    )

            except Exception as e:
                LOGGER.error(f'❌ Erro ao abrir caixa para {employee.id}: {e}')
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f'Erro ao tentar abrir o caixa [login_and_open]: {str(e)}',
                )

            # 3. GERAÇÃO DE TOKEN E CACHE PERSISTENTE (Substitui Session ID)
            access_token = create_access_token(str(employee.id))
            refresh_token = create_refresh_token(str(employee.id))

            LOGGER.info(
                f'🔑 Tokens gerados para {employee_name} - Access Token: {access_token[:20]}...'
            )

            # 🎯 CACHE: Armazenar os dados de autenticação/sessão no Redis com o token como chave
            cache_key = f'token:{access_token}'

            # Dados a serem salvos (usados para a validação rápida em get_current_employee)
            session_cache_data = {
                'id': employee.id,
                'email': employee.email,
                'empresa_id': company_id,
                'caixa_id': caixa.caixa_id,
                'username': employee.nome,
                'company_name': company_name,
            }

            # SET com expire time para segurança (24 horas)
            try:
                await client.setex(
                    cache_key,
                    86400,
                    json.dumps(session_cache_data, default=str),
                )  # 24 horas em segundos
                LOGGER.debug(f'💾 Cache salvo no Redis para {employee_name}')
            except Exception as e:
                LOGGER.warning(
                    f'⚠️  Falha ao salvar cache de token no Redis: {e}'
                )
                # Não quebra o fluxo, apenas loga o warning

            # 4. RETORNO DA RESPOSTA
            response_data = {
                'id': employee.id,
                'username': employee.nome,
                'email': employee.email,
                'value': float(user.valor_inicial),
                'empresa': company_name,
                'empresa_id': company_id,
                'tipo': 'funcionario',
                'message': message,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'bearer',
                'caixa_id': caixa.caixa_id,
                'caixa_status': caixa_status,
            }

            LOGGER.info(
                f'✅ Login finalizado com sucesso para {employee_name} - Caixa Status: {caixa_status}'
            )
            return response_data

        # --- ROTA: /logout ---
        @self.router.post('/logout')
        async def logout(
            current_user: SystemEmployees = Depends(get_current_employee),
            token: str = Depends(reuseable_oauth),
        ):
            """
            Faz logout, invalida o token no cache (blocklist) e fecha o caixa.

            Args:
                current_user: Usuário autenticado (via dependency)
                token: Token JWT atual (via dependency)

            Returns:
                dict: Status e mensagem de sucesso

            Raises:
                HTTPException: 500 em caso de erro crítico no fechamento do caixa
            """
            LOGGER.info(f'🚪 Iniciando logout para Func ID: {current_user.id}')

            # 1. INVALIDAÇÃO DO TOKEN NO CACHE (Blocklist/Remoção)
            cache_key = f'token:{token}'
            removed = await client.delete(cache_key)

            if removed == 0:
                LOGGER.debug(
                    'ℹ️  Token não encontrado em cache (já expirou ou foi removido).'
                )
            else:
                LOGGER.debug('✅ Token removido do cache com sucesso.')

            # 2. FECHAMENTO DO CAIXA
            try:
                # O filtro usa o ID do funcionário e o ID da empresa (validado pelo token)
                close_checkout = await Caixa.filter(
                    funcionario_id=current_user.id,
                    usuario_id=current_user.empresa_id,
                    aberto=True,
                ).update(
                    aberto=False,
                    atualizado_em=datetime.now(ZoneInfo('America/Sao_Paulo')),
                )

                if close_checkout > 0:
                    LOGGER.info(
                        f'✅ Caixa fechado com sucesso para Func ID: {current_user.id}'
                    )
                    return {
                        'status': status.HTTP_200_OK,
                        'message': 'Logout e caixa fechados com sucesso.',
                    }

                # Se o caixa já estava fechado:
                LOGGER.warning(
                    f'ℹ️  Logout OK, mas caixa já estava fechado para Func ID: {current_user.id}'
                )
                return {
                    'status': status.HTTP_200_OK,
                    'message': 'Logout realizado. O caixa já estava fechado.',
                }

            except Exception as e:
                LOGGER.error(
                    f'❌ Erro crítico ao fechar o caixa (Func ID: {current_user.id}): {e}'
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail='Erro interno ao finalizar o caixa.',
                )

        # --- ROTA: /validate (Otimizada) ---
        @self.router.get('/validate', response_model=ValidateTokenResponse)
        async def validate_token(
            current_user: SystemEmployees = Depends(get_current_employee),
        ):
            """
            Valida se o token JWT é válido e se o caixa está aberto, usando o cache.

            Args:
                current_user: Usuário autenticado (via dependency)

            Returns:
                ValidateTokenResponse: Status de validação e dados do caixa
            """
            LOGGER.debug(f'🔍 Validando token para Func ID: {current_user.id}')

            # O get_current_employee já validou o token, verificou o cache, e garantiu
            # que o usuário e a empresa existem. Agora, só checamos o status do caixa.

            # 1. VERIFICA SE O CAIXA ESTÁ ABERTO (último caixa aberto)
            caixa_aberto = (
                await Caixa.filter(
                    funcionario_id=current_user.id,
                    usuario_id=current_user.empresa_id,
                    aberto=True,
                )
                .order_by('-id')
                .first()
            )

            # 2. CONSTRUÇÃO DA RESPOSTA DE VALIDAÇÃO
            if caixa_aberto:
                message = 'Token e sessão válidos - Caixa aberto.'
                LOGGER.debug(
                    f'✅ Validação positiva para Func ID: {current_user.id} - Caixa ID: {caixa_aberto.caixa_id}'
                )
            else:
                message = 'Token válido, mas caixa não está aberto.'
                LOGGER.warning(
                    f'⚠️  Token válido mas caixa fechado para Func ID: {current_user.id}'
                )

            return ValidateTokenResponse(
                valid=True,
                user_id=current_user.id,
                username=current_user.username,
                empresa=current_user.company_name,
                empresa_id=current_user.empresa_id,
                caixa_aberto=bool(caixa_aberto),
                caixa_id=caixa_aberto.caixa_id if caixa_aberto else None,
                saldo_inicial=float(caixa_aberto.saldo_inicial)
                if caixa_aberto
                else None,
                message=message,
            )

        # --- ROTA: /caixa/status (Simplificada) ---
        @self.router.get('/caixa/status')
        async def get_caixa_status(
            current_user: SystemEmployees = Depends(get_current_employee),
        ):
            """
            Retorna o status atual do caixa do funcionário.

            Args:
                current_user: Usuário autenticado (via dependency)

            Returns:
                dict: Status detalhado do caixa ou mensagem de não encontrado

            Raises:
                HTTPException: 500 em caso de erro na consulta
            """
            LOGGER.debug(
                f'📊 Consultando status do caixa para Func ID: {current_user.id}'
            )

            try:
                caixa_aberto = await Caixa.filter(
                    funcionario_id=current_user.id,
                    usuario_id=current_user.empresa_id,
                    aberto=True,
                ).first()

                if caixa_aberto:
                    response_data = {
                        'caixa_aberto': True,
                        'caixa_id': caixa_aberto.caixa_id,
                        'saldo_inicial': caixa_aberto.saldo_inicial,
                        'saldo_atual': caixa_aberto.saldo_atual,
                        'aberto_em': caixa_aberto.criado_em,
                        'message': 'Caixa está aberto',
                    }
                    LOGGER.debug(
                        f'✅ Caixa encontrado: ID {caixa_aberto.caixa_id} para Func ID: {current_user.id}'
                    )
                    return response_data
                else:
                    LOGGER.debug(
                        f'ℹ️  Nenhum caixa aberto encontrado para Func ID: {current_user.id}'
                    )
                    return {
                        'caixa_aberto': False,
                        'message': 'Nenhum caixa aberto encontrado',
                    }

            except Exception as e:
                LOGGER.error(
                    f'❌ Erro ao verificar status do caixa para Func ID: {current_user.id}: {e}'
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail='Erro ao verificar status do caixa',
                )
