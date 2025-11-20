from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ✅ Import da nova estrutura
from qodo.conf.database import init_database, close_database
from qodo.logs.infos import LOGGER
from qodo.routes import setup_routes, get_api_metadata
from qodo.utils.dados_teste import create_mock_data_and_sell_all_stock


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação."""
    load_dotenv()

    # ✅ Inicializa banco usando a nova configuração
    if await init_database():
        LOGGER.info('✅ Banco de dados iniciado e tabelas criadas!')
        # await create_mock_data_and_sell_all_stock()  # Descomente se necessário
    else:
        LOGGER.error('❌ Falha ao inicializar banco de dados')
        raise RuntimeError('Não foi possível inicializar o banco de dados')

    yield

    await close_database()
    LOGGER.info('🧱 Banco de dados encerrado com sucesso.')


class Server:
    def __init__(self):
        # ✅ Usa os metadados configurados profissionalmente
        self.api = FastAPI(**get_api_metadata(), debug=True, lifespan=lifespan)

        self.setup_middlewares()
        self.setup_routes()

    def setup_middlewares(self):
        """Configura middlewares da aplicação."""
        origins = [
            'http://127.0.0.1:3000',
            'http://localhost:3000',
            'http://127.0.0.1:8000',
            'http://localhost:8000',
            'http://127.0.0.1:5000',
            'http://localhost:5000',
            'http://127.0.0.1:8080',
            'http://localhost:8080',
            'http://localhost:5173',  # Vite/React
            'http://127.0.0.1:5173',
        ]

        self.api.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
            allow_headers=['*'],
        )

    def setup_routes(self):
        """Configura todas as rotas de forma profissional."""
        # ✅ Método 1: Usando o setup_routes (RECOMENDADO)
        setup_routes(self.api)

        # ✅ Rotas adicionais específicas (se necessário)
        from qodo.routes.caixa.start_router import checkout

        self.api.include_router(checkout)

        # ✅ Health Check e informações do sistema
        self.setup_system_routes()

    def setup_system_routes(self):
        """Configura rotas do sistema e health checks."""

        @self.api.get('/', tags=['🏠 Sistema'])
        async def root():
            """Endpoint raiz com informações do sistema."""
            return {
                'message': '🚀 Qodo PDV API está rodando!',
                'version': '1.0.0',
                'status': 'online',
                'docs': '/docs',
                'redoc': '/redoc',
            }

        @self.api.get('/health', tags=['🏠 Sistema'])
        async def health_check():
            """Health check da aplicação."""
            return {
                'status': 'healthy',
                'timestamp': '2024-01-01T00:00:00Z',  # Usar datetime.utcnow() em produção
                'service': 'qodo-pdv-api',
                'version': '1.0.0',
            }

        @self.api.get('/api/v1/info', tags=['🏠 Sistema'])
        async def system_info():
            """Informações detalhadas do sistema."""
            return {
                'name': 'Qodo PDV',
                'version': '1.0.0',
                'description': 'Sistema completo de Ponto de Venda',
                'developer': 'Qodo Tech',
                'contact': 'dacruzgg01@gmail.com',
                'repository': 'https://github.com/Gilderlan0101/qodo-pdv',
                'endpoints': {
                    'auth': '/api/v1/auth',
                    'products': '/api/v1/produtos',
                    'sales': '/api/v1/carrinho',
                    'dashboard': '/api/v1/dashboard',
                    'payments': '/api/v1/pagamentos',
                },
            }

    def run(self, host: str = '0.0.0.0', port: int = 8000):
        """Inicia o servidor Uvicorn."""
        LOGGER.info(f'🚀 Iniciando servidor Qodo PDV em {host}:{port}')

        uvicorn.run(
            'qodo.main:app', 
            host=host,
            port=port,
            reload=True,
            log_level='info',
            access_log=True,
            use_colors=True,
        )


# Instância global do app para FastAPI
app = Server().api


def main():
    """
    Função principal para executar o servidor Qodo PDV.
    Esta função é usada pelo entry point do setup.py
    """
    print('🚀 Iniciando Qodo PDV Server...')
    print('📊 Sistema de Ponto de Venda - Qodo Tech')
    print('🔗 API disponível em: http://0.0.0.0:8000')
    print('📚 Documentação: http://0.0.0.0:8000/docs')
    print('🔍 Redoc: http://0.0.0.0:8000/redoc')
    print('❤️  Health Check: http://0.0.0.0:8000/health')
    print('⏹️  Para parar o servidor, pressione Ctrl+C')
    print('-' * 60)

    try:
        server = Server()
        server.run()
    except KeyboardInterrupt:
        print('\n🛑 Servidor interrompido pelo usuário')
    except Exception as e:
        print(f'❌ Erro ao iniciar servidor: {e}')
        LOGGER.error(f'Erro ao iniciar servidor: {e}')


if __name__ == '__main__':
    main()