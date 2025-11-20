from setuptools import setup, find_packages
import os

# Ler dependências do requirements.txt
def read_requirements():
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        return [
            line.strip()
            for line in f
            if line.strip() and not line.startswith('#')
        ]


# Ler README
def read_readme():
    if os.path.exists('README.md'):
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    return 'Qodo PDV - Sistema completo de Ponto de Venda'


setup(
    name='qodo',
    version='0.1.0',
    description='Sistema completo de PDV (Ponto de Venda) com múltiplos recursos e integrações',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='Qodo Tech',
    author_email='dacruzgg01@gmail.com',
    url='https://github.com/Gilderlan0101/qodo-pdv',
    
    # ✅ CORREÇÃO: Liste explicitamente os pacotes
    packages=[
        'qodo',
        'qodo.auth',
        'qodo.conf', 
        'qodo.controllers',
        'qodo.controllers.user',
        'qodo.controllers.products',
        'qodo.controllers.payments',
        'qodo.controllers.payments.partial',
        'qodo.core',
        'qodo.logs',
        'qodo.model',
        'qodo.routes',
        'qodo.routes.account',
        'qodo.routes.caixa',
        'qodo.routes.car',
        'qodo.routes.customer',
        'qodo.routes.delivery',
        'qodo.routes.fornecedor',
        'qodo.routes.marketplace',
        'qodo.routes.payments',
        'qodo.routes.products',
        'qodo.routes.products.inventario',
        'qodo.schemas',
        'qodo.schemas.customers',
        'qodo.schemas.delivery',
        'qodo.schemas.fornecedor',
        'qodo.schemas.funcs',
        'qodo.schemas.login',
        'qodo.schemas.payments',
        'qodo.services',
        'qodo.utils',
    ],
    package_dir={'': 'src'},
    
    # ✅ REMOVA package_data temporariamente
    # package_data={
    #     'qodo': ['*.md', '*.txt', 'static/logo/*.png'],
    # },
    include_package_data=True,
    
    install_requires=[
        'fastapi',
        'uvicorn',
        'sqlmodel',
        'pydantic',
        'pydantic-settings',
        'python-dotenv',
        'python-jose',
        'passlib',
        'httpx',
        'email-validator',
        'faker',
        'aiomysql',
        'bcrypt==4.3.0',
        'tortoise-orm',
        'redis',
        'requests',
        'fpdf',
        'jose',
        'python-multipart',
        'validate_docbr',
        'pydantic_br'
    ],
    
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'black>=22.0.0',
            'flake8>=4.0.0',
            'mypy>=1.0.0',
        ],
        'mysql': [
            'aiomysql>=0.2.0',
            'pymysql>=1.0.0',
        ],
        'sqlite': [
            'aiosqlite>=0.18.0',
        ],
    },
    
    entry_points={
        'console_scripts': [
            'qodo-pdv=qodo.main:main',
            'qodo-server=qodo.main:main',
        ],
    },
    
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Office/Business :: Financial :: Point-Of-Sale',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    
    keywords='pdv ponto-de-venda venda checkout fastapi sqlite mysql',
    python_requires='>=3.8',
    
    project_urls={
        'Documentation': 'https://github.com/Gilderlan0101/qodo-pdv',
        'Source': 'https://github.com/Gilderlan0101/qodo-pdv',
        'Tracker': 'https://github.com/Gilderlan0101/qodo-pdv/issues',
    },
)
