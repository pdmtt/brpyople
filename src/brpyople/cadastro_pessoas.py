"""
Código que manipula os registros dos cadastros de pessoas nacionais.
Atualmente, trata somente do Cadastro de Pessoas Físicas (CPF) e do Cadastro Nacional de Pessoas
Jurídicas (CNPJ).
"""
import re
from enum import Enum

REGEX_CPF_COM_SEPARADORES = re.compile(r'\d{3}\.\d{3}\.\d{3}-\d{2}')
REGEX_CPF_SEM_SEPARADORES = re.compile(r'\d{3}\d{3}\d{3}\d{2}')
REGEX_CNPJ_COM_SEPARADORES = re.compile(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}')
REGEX_CNPJ_SEM_SEPARADORES = re.compile(r'\d{2}\d{3}\d{3}\d{4}\d{2}')


class EspeciesCadastroPessoas(Enum):
    """Enumera as espécies do gênero cadastros de pessoas."""
    CNPJ = 0  # Cadastro Nacional de Pessoas Jurídicas (CNPJ)
    CPF = 1  # Cadastro Nacional de Pessoas Físicas (CPF)


class Registro:
    """
    Registro contido em alguma espécie de cadastro de pessoas.

    Todos os cadastros de pessoas consistem numa coleção de registros unicamente identificados. O
    valor que identifica um registro é chamado de "identificador" neste repositório.

    Cada cadastro de pessoa institui regras de validade para seus identificadores. Por exemplo,
    todos os identificadores de registro no Cadastro de Pessoas Físicas (CPF) devem conter 11
    dígitos e podem conter até dois pontos finais (.) e um hífen (-): "NNN.NNN.NNN-NN".

    Além disso, os dígitos finais tanto no CPF quanto no CNPJ são calculados a partir dos dígitos
    anteriores usando um algoritmo pré-determinado, assim possibilitando a identificação de erros de
    digitação.
    """

    def __init__(self, identificador: str, /) -> None:
        """
        :param identificador: O identificador do registro no cadastro de pessoas.
        :raise ValueError: Quando o identificador não se adequar ao padrão de nenhum cadastro de
            pessoas.
        """
        if not isinstance(identificador, str):
            raise TypeError('Argumento passado deve ser do tipo "str"')

        self.cadastro_pessoas: EspeciesCadastroPessoas
        """Qual o cadastro de pessoas a que o registro pertence."""

        self.digitos_identificador = re.sub(r'\D', '', identificador)
        """Os dígitos do identificador, após excluídos os separadores."""

        self.identificador_formatado: str
        """O identificador com os separadores."""

        self.identificador_valido: bool
        """O identificador é válido quando segue todas as regras do cadastro de pessoas."""

        # CPF
        if (
                REGEX_CPF_COM_SEPARADORES.fullmatch(identificador)
                or REGEX_CPF_SEM_SEPARADORES.fullmatch(identificador)
        ):
            self.cadastro_pessoas = EspeciesCadastroPessoas.CPF

            self.identificador_formatado = '.'.join((
                self.digitos_identificador[:3],
                self.digitos_identificador[3:6],
                self.digitos_identificador[6:9]
            )) + '-' + self.digitos_identificador[9:11]

            # Valida os dígitos-verificadores do identificador
            identificador_valido = self.digitos_identificador[:-2]
            for dv in (0, 1):
                soma = 0
                for char, multiplicador in zip(identificador_valido[dv:], range(10, 1, -1)):
                    soma += int(char) * multiplicador
                resto = soma % 11
                identificador_valido += str(11 - resto if resto > 1 else 0)

        # CNPJ
        elif (
                REGEX_CNPJ_COM_SEPARADORES.fullmatch(identificador)
                or REGEX_CNPJ_SEM_SEPARADORES.fullmatch(identificador)
        ):
            self.cadastro_pessoas = EspeciesCadastroPessoas.CNPJ

            estabelecimento = self.digitos_identificador[8:12]
            self.identificador_formatado = '.'.join((
                self.digitos_identificador[:2],
                self.digitos_identificador[2:5],
                self.digitos_identificador[5:8]
            )) + f'/{estabelecimento}-{self.digitos_identificador[12:]}'

            # Valida os dígitos-verificadores do identificador
            identificador_valido = (
                    self.digitos_identificador[:12]
                    + self._digitos_verificadores_identificador_registro_cnpj(
                        raiz=self.digitos_identificador[:8],
                        estabelecimento=int(estabelecimento)
                    )
            )

        else:
            raise ValueError(
                f'O identificador "{identificador}" não segue o padrão de algum cadastro de '
                'pessoas'
            )

        self.identificador_valido = identificador_valido == self.digitos_identificador

    @staticmethod
    def _digitos_verificadores_identificador_registro_cnpj(raiz: str, estabelecimento: int) -> str:
        """Retorna os dígitos-verificadores do identificador de um registro do CNPJ."""
        digitos_preditores = str(raiz) + str(estabelecimento).zfill(4)
        if len(digitos_preditores) != 12 or not digitos_preditores.isdigit():
            raise ValueError('É necessário um texto contendo apenas 12 dígitos exatamente')

        for _ in (1, 2):
            mult, soma = 9, 0
            for c in digitos_preditores[::-1]:
                soma += int(c) * mult
                mult = mult - 1 if mult > 2 else 9
            resto = soma % 11
            digitos_preditores += str(resto if resto != 10 else 0)

        return digitos_preditores[-2:]

    @classmethod
    def estabelecimento_com_raiz_cnpj(cls, raiz: str, estabelecimento: int = 1) -> "Registro":
        """
        Fábrica que retorna um :class:`Registro` do CNPJ e com identificador válido contendo
        a raiz e o estabelecimento requisitado.

        Exemplos:
            - ('00000000', 1) → <Registro('00.000.000/0001-91')>
            - ('00000000', 2) → <Registro('00.000.000/0002-72')>

        Os identificadores dos registros do CNPJ seguem o padrão "RR.RRR.RRR/MMMM-VV".
        Os oitos primeiros dígitos ("R") consistem na "raiz" do identificador.
        Os quatro seguintes ("M"), "estabelecimento".
        Os dois últimos ("V"), "dígitos verificadores".

        O estabelecimento "1" é sempre da matriz/sede e os demais, das filiais.
        """
        if int(estabelecimento) < 1:
            raise ValueError('Não existe estabelecimento menor que 1')

        return cls(
            raiz
            + str(estabelecimento).zfill(4)
            + cls._digitos_verificadores_identificador_registro_cnpj(raiz, estabelecimento)
        )
