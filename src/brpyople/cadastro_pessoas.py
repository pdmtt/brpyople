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
REGEX_RAIZ_CNPJ = re.compile(r'\d{8}')


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

    @staticmethod
    def gerar_digitos_verificadores(texto: str, cadastro_pessoas: EspeciesCadastroPessoas) -> str:
        """
        Gera corretamente os dígitos-verificadores do texto passado, interpretado como um
        identificador de registro, seguindo o algoritmo do cadastro de pessoas especificado.
        :param texto: Texto que deve conter a quantidade esperada de dígitos para o identificador do
            cadastro de pessoas escolhido. Também admite que o texto recebido não tenha os dois
            últimos dígitos, pois seriam os dígitos-verificadores que serão gerados.
            Pode conter os separadores, que serão ignorados.
            Qualquer outro caracter fará a função levantar erro.
        :param cadastro_pessoas: Qual o cadastro de pessoas a que pertence o identificador contido
            no texto.
        """
        texto_sem_separadores = re.sub(r'[./-]', '', texto)

        # Valida o texto passado
        try:
            quantidade_maxima_digitos = {
                EspeciesCadastroPessoas.CNPJ: 14,
                EspeciesCadastroPessoas.CPF: 11,
            }[cadastro_pessoas]
        except KeyError:
            raise ValueError('Cadastro de pessoas inesperado')

        if (
                len(texto_sem_separadores) not in (
                    quantidade_maxima_digitos,
                    quantidade_maxima_digitos - 2  # Excluindo os dígitos-verificadores
                )
                or not texto_sem_separadores.isdigit()  # Se existir algum caractere não-dígito
        ):
            raise ValueError(
                f'O texto "{texto}" ou não contém a quantidade esperada de dígitos, ou contém pelo '
                'menos um caractere que não é dígito'
            )

        # Gera o dígitos-verificadores.
        if len(texto_sem_separadores) == quantidade_maxima_digitos:
            # Remove os últimos dois dígitos, os dígitos-verificadores, quando incluídos no texto.
            identificador_valido = texto_sem_separadores[:-2]
        else:
            identificador_valido = texto_sem_separadores

        if cadastro_pessoas == EspeciesCadastroPessoas.CPF:
            for dv in (0, 1):
                soma = 0
                for char, multiplicador in zip(identificador_valido[dv:], range(10, 1, -1)):
                    soma += int(char) * multiplicador
                resto = soma % 11
                identificador_valido += str(11 - resto if resto > 1 else 0)

        else:
            for _ in (1, 2):
                mult, soma = 9, 0
                for c in identificador_valido[::-1]:
                    soma += int(c) * mult
                    mult = mult - 1 if mult > 2 else 9
                resto = soma % 11
                identificador_valido += str(resto if resto != 10 else 0)

        return identificador_valido[-2:]

    @classmethod
    def de_estabelecimento_com_raiz_cnpj(cls, raiz: str, estabelecimento: int = 1) -> "Registro":
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

        texto_gerar_digitos = raiz + str(estabelecimento).zfill(4)

        return cls(
            texto_gerar_digitos
            + cls.gerar_digitos_verificadores(texto_gerar_digitos, EspeciesCadastroPessoas.CNPJ)
        )

    def __init__(self, identificador: str) -> None:
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

        # CNPJ
        elif (
                REGEX_CNPJ_COM_SEPARADORES.fullmatch(identificador)
                or REGEX_CNPJ_SEM_SEPARADORES.fullmatch(identificador)
        ):
            self.cadastro_pessoas = EspeciesCadastroPessoas.CNPJ

            self.identificador_formatado = '.'.join((
                self.digitos_identificador[:2],
                self.digitos_identificador[2:5],
                self.digitos_identificador[5:8]
            )) + f'/{self.digitos_identificador[8:12]}-{self.digitos_identificador[12:]}'

        else:
            raise ValueError(
                f'O identificador "{identificador}" não segue o padrão de qualquer cadastro de '
                'pessoas'
            )

        # O identificador é considerado válido se os seus dígitos-verificadores tiverem sido gerados
        # conforme o algoritmo designado para cada cadastro de pessoas.
        self.identificador_valido = self.gerar_digitos_verificadores(
            self.digitos_identificador,
            self.cadastro_pessoas
        ) == self.digitos_identificador[-2:]

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.identificador_formatado})'

    def extrair_raiz_cnpj(self) -> str:
        """
        Retorna um texto contendo somente os oito primeiros dígitos do identificador do registro, se
        ele for vinculado ao CNPJ.

        Todos os identificadores vinculados a uma mesma entidade cadastrada no CNPJ têm a mesma
        raiz.
        :raise ValueError: Se o registro não pertencer ao CNPJ.
        """
        if self.cadastro_pessoas is not EspeciesCadastroPessoas.CNPJ:
            raise ValueError(
                'Somente registros vinculados ao CNPJ podem ter a raiz do seu identificador '
                'extraída'
            )
        return self.digitos_identificador[:8]
