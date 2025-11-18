
# CB2325NumericaG07

[](https://www.google.com/search?q=https://pypi.org/project/CB2325NumericaG07/)
[](https://opensource.org/licenses/MIT)

Uma biblioteca de Cálculo Numérico desenvolvida em Python, com recursos gráficos integrados.

-----

> **Contexto Acadêmico:**
>
> Este projeto foi desenvolvido pelo **Grupo 07** como trabalho final para a disciplina **CB23 - Prog 02 (2025)**, ministrada pelo Prof. Emilio Brazil.
>
> O objetivo principal é implementar os métodos numéricos centrais estudados em classe, encapsulando-os em uma biblioteca Python reutilizável, documentada e distribuída no PyPI.

## Instalação

Você pode instalar a biblioteca diretamente do PyPI usando `pip`:

```bash
pip install CB2325NumericaG07
```

## Funcionalidades Principais

Esta biblioteca cumpre todos os requisitos do projeto, implementando módulos para:

* **Raízes de Funções**

* **Interpolação**

* **Aproximação de Funções**

* **Integração Numérica**

* **Erros Numéricos**

Todos os módulos que produzem saídas visuais (ex: `Interpolação` ou `Aproximação`) possuem parâmetros para gerar gráficos usando `matplotlib`.

## Exemplo Rápido (Tutorial Rápido)

Veja como é simples encontrar raízes de funções ou interpolar uma nuvem de pontos.

### Exemplo 1: Encontrando uma Raiz (Newton-Raphson)

```python
# Importando o módulo de raízes
from CB2325NumericaG07.raizes import newton_raphson

# Definindo a função f(x) = x² - 9x + 5
função = lambda x: x**2 - 9*x + 5

tol = 1/100 # Definindo tolerância

resultado = metodo_newton_raphson(função, tol)

print(f'Valor calculado foi {resultado}')
# Saída esperada: Valor calculado foi 0.5948752170638366
```

### Exemplo 2: Interpolação de Pontos (Hermite)

```python
from CB2325NumericaG07.interpolacao import interpolacao_de_hermite 

x_hermite = [0, 1, 4, 6, 8]
y_hermite = [0, 1, 2, 4, 2]

print('Hermite')
funcao_interpolada_h = interpolacao_de_hermite(x_hermite, y_hermite, plot=True)

ponto_teste_h = 0.5
valor_interpolado_h = funcao_interpolada_h(ponto_teste_h)

print(f"Pontos x: {x_hermite}")
print(f"Pontos y: {y_hermite}")
print(f"f(x) interpolado em x={ponto_teste_h}: {valor_interpolado_h}")

#Saida esperada: 
#Hermite
#Pontos x: [0, 1, 4, 6, 8]
#Pontos y: [0, 1, 2, 4, 2]
#f(x) interpolado em x=0.5: 0.6149757407960439
```
![alt text](docs/images/image.png)


## Estrutura do Projeto

O repositório está organizado conforme os requisitos do trabalho:

```txt
CB2325NumericaG07/
├── CB2325NumericaG07/      # O pacote python (código fonte)
│   ├── __init__.py
│   ├── raizes.py
│   ├── interpolacao.py
│   ├── aproximacao.py
│   └── integracao.py
|   └── erros.py
├── docs/                 # Documentação em Markdown
│   └── aproximacao.md
|   └── ...
├── notebooks_demos/      # Notebooks Jupyter com exemplos de uso
|   └── integracao_demo.ipynb
|   └── ...
├── testes_unitarios/     # Arquivos .py para test com pytest
|   └── test_interpolacao.py
|   └── ...
├── README.md             # Este arquivo
├── pyproject.toml        # Configuração do pacote
├── LICENSE
├── MANIFEST.in           # Para pypi
├── requirements.txt      # Para pip
└── .gitignore
```

## Autores (Grupo 07)

  * Gabriel Da Silva Rodrigues
  * Josiete Morais Santos Silva
  * José Armando Silva Duarte
  * Kayky Lopes Teixeira Martins
  * Lucas Mourão Cerqueira E Silva
  * Lucca Moulin Cruz
  * Marcella Decembrino De Souza
  * Maria Izabelle Sousa Da Silva
  * **Mateus Bandeira De Mello Torres**
  * Rhuan Soler De Almeida

## Licença

Este projeto é licenciado sob a Licença MIT. Veja o arquivo `pyproject.toml` para mais detalhes.
