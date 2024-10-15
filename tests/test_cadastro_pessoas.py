"""Testa os objetos implementados em brpyople.cadastro_pessoas."""
import pytest

from brpyople.cadastro_pessoas import Registro, EspeciesCadastroPessoas


@pytest.fixture(params=[
    ("070.680.938-68", EspeciesCadastroPessoas.CPF, "070.680.938-68"),
    ("07068093868", EspeciesCadastroPessoas.CPF, "070.680.938-68"),
    ("453.178.287-91", EspeciesCadastroPessoas.CPF, "453.178.287-91"),
    ("45317828791", EspeciesCadastroPessoas.CPF, "453.178.287-91"),
    ("00.000.000/0001-91", EspeciesCadastroPessoas.CNPJ, "00.000.000/0001-91"),
    ("00000000000191", EspeciesCadastroPessoas.CNPJ, "00.000.000/0001-91")
])
def dados_identificador_valido(request) -> tuple[str, EspeciesCadastroPessoas, str]:
    """
    Dados relacionados a um identificador válido.

    Tupla contendo três objetos:
        - Texto contendo identificador para ser passado ao construtor do :class:`Registro`
        - O cadastro de pessoas a que pertence o identificador
        - Texto contendo o identificador formatado, ou seja, com separadores
    """
    return request.param[0], request.param[1], request.param[2]


def test_registro_valido(dados_identificador_valido) -> None:
    identificador, cadastro_pessoas, identificador_formatado = dados_identificador_valido

    registro = Registro(identificador)
    assert registro.cadastro_pessoas == cadastro_pessoas
    assert registro.identificador_valido
    assert registro.identificador_formatado == identificador_formatado


@pytest.fixture(params=[
    ("070.680.938-61", EspeciesCadastroPessoas.CPF),
    ("07068093861", EspeciesCadastroPessoas.CPF),
    ("453.178.287-92", EspeciesCadastroPessoas.CPF),
    ("45317828792", EspeciesCadastroPessoas.CPF),
    ("00.000.000/0001-93", EspeciesCadastroPessoas.CNPJ),
    ("00000000000193", EspeciesCadastroPessoas.CNPJ)
])
def dados_identificador_invalido(request) -> tuple[str, EspeciesCadastroPessoas]:
    """
    Dados relacionados a um identificador inválido.

    Tupla contendo dois objetos:
        - Texto contendo identificador para ser passado ao construtor do :class:`Registro`
        - O cadastro de pessoas a que pertence o identificador
    """
    return request.param[0], request.param[1]


def test_registro_invalido(dados_identificador_invalido) -> None:
    identificador, cadastro_pessoas = dados_identificador_invalido

    registro = Registro(identificador)
    assert registro.cadastro_pessoas == cadastro_pessoas
    assert not registro.identificador_valido


@pytest.fixture(params=[
    ('00000000', 1, '00.000.000/0001-91'),
    ('00000000', 2, '00.000.000/0002-72'),
])
def dados_fabrica_usando_raiz_cnpj(request) -> tuple[str, int, str]:
    """
    Dados que serão usados como argumentos da função que fabrica :class:`Registro` a partir da raiz
    de um identificador do CNPJ.

    Tupla contendo três objetos:
        - Texto contendo a raiz do identificador do CNPJ
        - Número do estabelecimento
        - Texto contendo o identificador formatado gerado a partir dos outros dois objetos
    """
    return request.param


def test_registro_estabelecimento_com_raiz_cnpj(dados_fabrica_usando_raiz_cnpj):
    raiz_identificador, n_estabelecimento, identificador_formatado = dados_fabrica_usando_raiz_cnpj

    with pytest.raises(ValueError):
        Registro(raiz_identificador)

    registro = Registro.de_estabelecimento_com_raiz_cnpj(
        raiz=raiz_identificador,
        estabelecimento=n_estabelecimento
    )

    assert registro.identificador_formatado == identificador_formatado
    assert registro.extrair_raiz_cnpj() == raiz_identificador
