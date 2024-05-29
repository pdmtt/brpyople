import pytest

from brpyople.cadastro_pessoas import Registro, Especies


@pytest.fixture(params=[
    ("070.680.938-68", Especies.CPF, "070.680.938-68"),
    ("07068093868", Especies.CPF, "070.680.938-68"),
    ("453.178.287-91", Especies.CPF, "453.178.287-91"),
    ("45317828791", Especies.CPF, "453.178.287-91"),
    ("00.000.000/0001-91", Especies.CNPJ, "00.000.000/0001-91"),
    ("00000000000191", Especies.CNPJ, "00.000.000/0001-91")
])
def identificador_valido_e_cadastro(request) -> tuple[str, Especies, str]:
    return request.param[0], request.param[1], request.param[2]


def test_registro_valido(identificador_valido_e_cadastro) -> None:
    registro = Registro(identificador_valido_e_cadastro[0])
    assert registro.cadastro_pessoas == identificador_valido_e_cadastro[1]
    assert registro.identificador_valido
    assert registro.identificador_formatado == identificador_valido_e_cadastro[2]


@pytest.fixture(params=[
    ("070.680.938-61", Especies.CPF),
    ("07068093861", Especies.CPF),
    ("453.178.287-92", Especies.CPF),
    ("45317828792", Especies.CPF),
    ("00.000.000/0001-93", Especies.CNPJ),
    ("00000000000193", Especies.CNPJ)
])
def identificador_invalido_e_cadastro(request) -> tuple[str, Especies]:
    return request.param[0], request.param[1]


def test_registro_invalido(identificador_invalido_e_cadastro) -> None:
    registro = Registro(identificador_invalido_e_cadastro[0])
    assert registro.cadastro_pessoas == identificador_invalido_e_cadastro[1]
    assert not registro.identificador_valido
    assert registro.razao_invalidez_identificador == 'Dígitos verificadores inválidos'
