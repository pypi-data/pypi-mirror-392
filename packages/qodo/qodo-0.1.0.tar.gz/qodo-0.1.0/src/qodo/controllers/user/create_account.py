from typing import Optional

from pydantic import EmailStr
from tortoise.transactions import in_transaction

from qodo.logs.infos import LOGGER
from qodo.model.user import Usuario
from qodo.model.cnpjCache import CNPJCache


class CreateCompany:

    # Dados Inicias
    def __init__(
        self,
        # Dados pessoais
        full_name: str,
        email: EmailStr,
        password: str,
        cpf: Optional[str] = None,
        phone: Optional[str] = None,
        # Dados da empresa
        cnpj: Optional[str] = None,
        company_name: Optional[str] = None,
        trade_name: Optional[str] = None,
        state_registration: Optional[str] = None,
        municipal_registration: Optional[str] = None,
        cnae_pricipal: Optional[str] = None,
        crt: Optional[int] = None,
        # Endereço
        cep: Optional[str] = None,
        street: Optional[str] = None,
        number: Optional[str] = None,
        complement: Optional[str] = None,
        district: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
    ):

        # Dados pessoais
        self.full_name = full_name
        self.email = email
        self.password = password
        self.cpf = cpf
        self.phone = phone
        # Dados da empresa
        self.cnpj = cnpj
        self.company_name = company_name
        self.trade_name = trade_name
        self.state_registration = state_registration
        self.municipal_registration = municipal_registration
        self.cnae_pricipal = cnae_pricipal
        self.crt = crt
        # Endereço
        self.cep = cep
        self.street = street
        self.number = number
        self.complement = complement
        self.district = district
        self.city = city
        self.state = state

    async def new_company(self) -> list[dict[str, any]]:
        """Metodo para cadastra uma nova empresa"""

        try:
            # Antes de cadastra crie uma hash da senha
            from qodo.auth.auth_jwt import get_hashed_password

            hashed_password = get_hashed_password(self.password)

            # Cadastra uma empresa
            data_company = await Usuario(
                username=self.full_name,
                email=self.email,
                password=hashed_password,
                company_name=self.company_name,
                trade_name=self.trade_name,
                membros=0,  # Quantidade de filias Default 0
                cpf=self.cpf,
                cnpj=self.cnpj,
                state_registration=self.state_registration,
                municipal_registration=self.municipal_registration,
                cnae_pricipal=self.cnae_pricipal,
                crt=self.crt,
                cep=self.cep,
                street=self.street,
                number=self.number,
                complement=self.complement,
                district=self.district,
                city=self.city,
                state=self.state,
            )

            await data_company.save()

            # Retorno seguro (sem senha)
            return {
                'id': data_company.id,
                'username': data_company.username,
                'email': data_company.email,
                'empresa': data_company.company_name,
                'criado_em': data_company.criado_em.strftime(
                    '%d/%m/%Y %H:%M:%S'
                ),
            }

        except Exception as e:
            LOGGER.error(
                f'Erro ao cadastra uma empresa: {e} [{e.__traceback__.tb_lineno}]'
            )
            return None
