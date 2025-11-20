# src/conf/database.py
import asyncio
import os
from typing import Optional, Dict, Any

from dotenv import load_dotenv
from tortoise import Tortoise
from tortoise.exceptions import ConfigurationError

# Carregar variáveis de ambiente
load_dotenv()


class DatabaseConfig:
    """Classe para configuração flexível do banco de dados"""

    @staticmethod
    def get_sqlite_config(db_path: str = 'qodo_pdv.db') -> Dict[str, Any]:
        """Retorna configuração para SQLite"""
        return {
            'connections': {
                'default': {
                    'engine': 'tortoise.backends.sqlite',
                    'credentials': {
                        'file_path': db_path,
                    },
                }
            },
            'apps': {
                'models': {
                    'models': [
                        # ✅ LISTA EXPLÍCITA de todos os modelos
                        'qodo.model.user',
                        'qodo.model.employee',
                        'qodo.model.customers',
                        'qodo.model.caixa',
                        'qodo.model.cashmovement',
                        'qodo.model.sale',
                        'qodo.model.partial',
                        'qodo.model.carItems',
                        'qodo.model.product',
                        'qodo.model.fornecedor',
                        'qodo.model.membros',
                        'qodo.model.cnpjCache',
                        'qodo.model.tickets',
                        'qodo.model.delivery',
                        'qodo.model.pix',
                    ],
                    'default_connection': 'default',
                }
            },
            'use_tz': False,
            'timezone': 'America/Sao_Paulo',
        }

    @staticmethod
    def get_mysql_config() -> Optional[Dict[str, Any]]:
        """Retorna configuração para MySQL se as variáveis estiverem disponíveis"""
        DB_USER = os.getenv('DB_USER')
        DB_PASS = os.getenv('DB_PASS')
        DB_HOST = os.getenv('DB_HOST')
        DB_PORT = os.getenv('DB_PORT', '3306')
        DB_NAME = os.getenv('DB_NAME')

        if all([DB_USER, DB_PASS, DB_HOST, DB_NAME]):
            return {
                'connections': {
                    'default': {
                        'engine': 'tortoise.backends.mysql',
                        'credentials': {
                            'host': DB_HOST,
                            'port': int(DB_PORT),
                            'user': DB_USER,
                            'password': DB_PASS,
                            'database': DB_NAME,
                            'charset': 'utf8mb4',
                        },
                    }
                },
                'apps': {
                    'models': {
                        'models': [
                            # ✅ MESMA LISTA para MySQL
                            'qodo.model.user',
                            'qodo.model.employee',
                            'qodo.model.customers',
                            'qodo.model.caixa',
                            'qodo.model.cashmovement',
                            'qodo.model.sale',
                            'qodo.model.partial',
                            'qodo.model.carItems',
                            'qodo.model.product',
                            'qodo.model.fornecedor',
                            'qodo.model.membros',
                            'qodo.model.cnpjCache',
                            'qodo.model.tickets',
                            'qodo.model.delivery',
                            'qodo.model.pix',
                        ],
                        'default_connection': 'default',
                    }
                },
                'use_tz': False,
                'timezone': 'America/Sao_Paulo',
            }
        return None


async def init_database(config: Optional[Dict[str, Any]] = None) -> bool:
    """
    Inicializa o banco de dados
    """
    try:
        if config is None:
            config = DatabaseConfig.get_sqlite_config()

        print(
            f"🔧 Configurando banco: {config['connections']['default']['engine']}"
        )
        print(
            f"📋 Modelos carregados: {len(config['apps']['models']['models'])}"
        )

        await Tortoise.init(config=config)
        print('✅ Tortoise ORM inicializado!')

        # Cria as tabelas se não existirem
        await Tortoise.generate_schemas()
        print('✅ Tabelas criadas/verificadas!')

        return True

    except ConfigurationError as e:
        print(f'❌ Erro de configuração do Tortoise: {e}')
        return False
    except Exception as e:
        print(f'❌ Erro ao inicializar banco: {e}')
        import traceback

        print(f'📋 Detalhes: {traceback.format_exc()}')
        return False


async def close_database():
    """Fecha as conexões do banco"""
    try:
        await Tortoise.close_connections()
        print('✅ Conexões do banco fechadas!')
    except Exception as e:
        print(f'⚠️  Aviso ao fechar conexões: {e}')


async def get_database_connection():
    """Retorna a conexão com o banco"""
    return Tortoise.get_connection('default')
