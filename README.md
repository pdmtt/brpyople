# brpyople

Código em Python para tratar e manipular dados que identificam pessoas brasileiras, sejam elas 
pessoas físicas, sejam pessoas jurídicas.

O nome era para ser um trocadilho com `PEOPLE`. Pessoas... brasileiras...

## Utilização básica
```pycon
>>> from brpyople import RegistroCadastroPessoas
>>> cpf_valido = RegistroCadastroPessoas("07068093868")
>>> cpf_valido.identificador_valido
True
>>> cpf_valido.identificador_formatado
'070.680.938-68'
>>> cpf_valido.cadastro_pessoas
<Especies.CPF: 1>
```

## Conceitos
### Cadastro de pessoas
A União instituiu e administra dois cadastros centrais de pessoas no Brasil: o Cadastro de Pessoas 
Físicas (CPF) e o Cadastro de Pessoas Jurídicas (CNPJ). Cada um desses cadastros é uma espécie do 
gênero "cadastro de pessoas".

Ambas consistem numa coleção de registros unicamente identificados. O valor que identifica cada 
registro é chamado de "identificador" neste pacote.

Cada cadastro de pessoa institui regras de validade para seus identificadores. Por exemplo,
todos os identificadores de registro no Cadastro de Pessoas Físicas (CPF) devem conter 11
dígitos e podem conter até dois pontos finais (.) e um hífen (-): "NNN.NNN.NNN-NN".

Além disso, os dígitos finais, tanto no CPF, quanto no CNPJ, são calculados a partir dos dígitos
anteriores, usando algum algoritmo pré-determinado, assim possibilitando a identificação de
erros de digitação.

### Pessoas
Pessoas são o que está registrado nos cadastros de pessoas.