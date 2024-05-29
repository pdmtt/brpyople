import re
from enum import Enum


class Especies(Enum):
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

    Além disso, os dígitos finais, tanto no CPF, quanto no CNPJ, são calculados a partir dos dígitos
    anteriores, usando algum algoritmo pré-determinado, assim possibilitando a identificação de
    erros de digitação.
    """

    def __init__(self, _identificador: str, /) -> None:
        if not isinstance(_identificador, str):
            raise TypeError('Argumento passado deve ser do tipo "str"')

        self.digitos_identificador = re.sub(r'\D', '', _identificador)

        if (
                len(re.sub(r'[^a-zA-Z]', '', _identificador)) > 0
                or len(self.digitos_identificador) not in (8, 11, 14)
        ):
            self.identificador_valido = False
            self.razao_invalidez_identificador = (
                f'Argumento "{_identificador}" contém ou caracteres alfabéticos, ou uma quantidade '
                'inadequada de dígitos'
            )

        if len(self.digitos_identificador) == 11:  # CPF
            self.cadastro_pessoas = Especies.CPF
            self.identificador_formatado = '.'.join((
                self.digitos_identificador[:3],
                self.digitos_identificador[3:6],
                self.digitos_identificador[6:9]
            )) + '-' + self.digitos_identificador[9:11]

            digitos_preditores = self.digitos_identificador[:-2]
            for dv in (0, 1):
                soma = 0
                for char, multiplicador in zip(digitos_preditores[dv:], range(10, 1, -1)):
                    soma += int(char) * multiplicador
                resto = soma % 11
                digitos_preditores += str(11 - resto if resto > 1 else 0)

        else:  # CNPJ
            self.cadastro_pessoas = Especies.CNPJ
            self.identificador_formatado = '.'.join((
                self.digitos_identificador[:2],
                self.digitos_identificador[2:5],
                self.digitos_identificador[5:8]
            )) + f'/{self.digitos_identificador[8:12]}-{self.digitos_identificador[12:]}'

            digitos_preditores = self.digitos_identificador[:12]
            for _ in (1, 2):
                mult, soma = 9, 0
                for c in digitos_preditores[::-1]:
                    soma += int(c) * mult
                    mult = mult - 1 if mult > 2 else 9
                resto = soma % 11
                digitos_preditores += str(resto if resto != 10 else 0)

        if digitos_preditores == self.digitos_identificador:
            self.identificador_valido = True
        else:
            self.identificador_valido = False
            self.razao_invalidez_identificador = "Dígitos verificadores inválidos"
