# `erros.py` — Módulo de Cálculo de Erros

Este módulo fornece funções para calcular erro absoluto e erro relativo entre dois valores numéricos.  

## Funcionalidades

### `erro_absoluto(valor_real, valor_aprox)`
Calcula o erro absoluto, definido como:
        erro absoluto= |valor real(aceito) - valor aproximado|

Retorna sempre o módulo dessa diferença.

### `erro_relativo(valor_real, valor_aprox)`
Calcula o erro relativo, definido como:

        erro relativo = |valor real - valor aproximado| / |valor real|

Casos especiais tratados:
- Se `valor_real == 0` e `valor_aprox == 0`, retorna `0.0`.
- Se `valor_real == 0` e `valor_aprox != 0`, retorna infinito (`float('inf')`).

## Exemplos de Uso

```python
from erros import erro_absoluto, erro_relativo

print(erro_absoluto(10, 9.6))#Deve exibir: 0.4
print(erro_relativo(10, 9.6))#Deve exibir: 0.04

print(erro_relativo(0, 0))#Deve exibir: 0.0
print(erro_relativo(0, 5))#Deve exibir: inf
