# Módulo: Raízes de Funções (`raizes.py`)

Este módulo implementa métodos numéricos fundamentais para a determinação de raízes de funções reais $f(x) = 0$, incluindo visualização gráfica.

## Funcionalidades

* **Método da Bisseção**: Método intervalar que garante a convergência (desde que o intervalo inicial contenha uma raiz).
* **Método da Secante**: Método iterativo rápido que utiliza a inclinação da reta secante para aproximar a raiz.
* **Método Newton-Raphson**: Método iterativo que utiliza a reta tangente para aproximar a raiz
* **Visualização Gráfica**: Plotagem automática da função e dos pontos de iteração utilizando `matplotlib`.
* **grid_search** :  Função que retorna intervalos menores para procura as raizes.

---

## Como Utilizar

Para utilizar as funções deste módulo, importe-as diretamente do pacote da biblioteca.

```python
from CB2325NumericaG07.raizes import metodo_bissecao, metodo_secante, metodo_newton_raphson
````

-----

## Documentação das Funções

### 1\. `metodo_bissecao`

Encontra a raiz de uma função $f(x)$ bisseccionando repetidamente um intervalo $[a, b]$ e selecionando o subintervalo onde a raiz deve estar.

**Sintaxe:**

```python
metodo_bissecao(f, a, b, tol=1e-6, max_inter=100, plotar=False)
```

**Parâmetros:**

  * `f` (*callable*): A função objetiva $f(x)$. Deve receber um float e retornar um float.
  * `a` (*float*): Limite inferior do intervalo inicial.
  * `b` (*float*): Limite superior do intervalo inicial.
      * *Requisito:* $f(a)$ e $f(b)$ devem ter sinais opostos ($f(a) \cdot f(b) < 0$).
  * `tol` (*float*, opcional): Tolerância para o critério de parada baseada na largura do intervalo ($|b - a| < tol$). Padrão: `1e-6`.
  * `max_inter` (*int*, opcional): Número máximo de iterações permitidas para evitar loops infinitos. Padrão: `100`.
  * `plotar` (*bool*, opcional): Se `True`, gera e exibe um gráfico ao final da execução mostrando a função e os pontos médios calculados.

**Retorno:**

  * `float`: A aproximação da raiz encontrada.
  * `None`: Se o método não convergir dentro de `max_inter` iterações.

**Levanta Erros (Raises):**

  * `ValueError`: Se $f(a)$ e $f(b)$ tiverem o mesmo sinal.

-----

### 2\. `metodo_secante`

Encontra a raiz de uma função $f(x)$ utilizando uma sucessão de raízes de linhas secantes para melhor aproximar a raiz da função.

**Sintaxe:**

```python
metodo_secante(f, x0, x1, tol=1e-6, max_inter=100, plotar=False)
```

**Parâmetros:**

  * `f` (*callable*): A função objetiva $f(x)$.
  * `x0` (*float*): Primeira estimativa inicial.
  * `x1` (*float*): Segunda estimativa inicial.
  * `tol` (*float*, opcional): Tolerância para o critério de parada ($|x_1 - x_0| < tol$). Padrão: `1e-6`.
  * `max_inter` (*int*, opcional): Número máximo de iterações permitidas. Padrão: `100`.
  * `plotar` (*bool*, opcional): Se `True`, gera e exibe um gráfico ao final mostrando a função e a trajetória das iterações.

**Retorno:**

  * `float`: A aproximação da raiz encontrada.
  * `None`: Se o método não convergir dentro de `max_inter` iterações.

**Levanta Erros (Raises):**

  * `ValueError`: Se ocorrer divisão por zero (`f(x1) == f(x0)`) durante o cálculo.

------
### 3\. `metodo_newton_raphson`

  Encontra a raiz de uma função $f(x)$ bisseccionando repetidamente um intervalo $[a, b]$ e selecionando o subintervalo onde a raiz deve estar.

**Sintaxe:**

```python
metodo_newton_raphson(função, tol=1e-6, max_iter=100, plotar=False, estimativa_inicial=None)
```

**Parâmetros:**

  * `função` (*callable*): A função objetiva $f(x)$.
  * `tol` (*float*, opcional): Tolerância para o critério de parada. Número utilizado para derivação numérica. Padrão: `1e-6`.
  * `max_iter` (*int*, opcional): Número máximo de iterações permitidas para evitar loops infinitos. Padrão: `100`.
  * `plotar` (*bool*, opcional): Se `True`, gera e exibe um gráfico ao final da execução mostrando a função e os pontos médios calculados.
  * `estimativa_inicial` (float, opcional): Primeira estimativa que o método irá testar para achar a raiz. O padrão é uma estimativa automática de baixa precisão. 

**Retorno:**

  * `float`: A aproximação da raiz encontrada. Caso o método não convirja, imprime uma mensagem.

**Levanta Erros (Raises):**

  * `ValueError`: Se 'função' não for callable ou se `max_iter`/`tol` tiverem valores inválidos.


------

### 4\. `grid_search`

Encontra os intervalos para calcular as raizes de uma função em um intervalo grande.

**Parâmetros:**

  * `func` (*callable*) : A função que queremos achar as raizes.
  * `a` (*float*) : Inicio do intervalo.
  * `b` (*float*) : Fim do intervalo.
  * `n` (*int*, opicional) : Quantidade de subdivisões para a procura dos intervalos 

**Retorno**

  * `list` : Lista com os sub-intervalos que contem as raizes. 

-----

## Exemplos Práticos

### Exemplo 1: Bisseção com Gráfico

```python
import matplotlib.pyplot as plt
from CB2325NumericaG07.raizes import metodo_bissecao

# Função: f(x) = x^3 - 9x + 5
f = lambda x: x**3 - 9*x + 5

# Busca a raiz no intervalo [0, 2] com gráfico ativado
raiz = metodo_bissecao(f, 0, 2, tol=1e-6, plotar=True)

print(f"Raiz encontrada: {raiz:.6f}")
# Saída esperada: aprox. 0.576888
```

### Exemplo 2: Secante

```python
import math
from CB2325NumericaG07.raizes import metodo_secante

# Função: f(x) = e^x - 4x
g = lambda x: math.exp(x) - 4*x

# Busca raiz começando com 0 e 1
raiz_sec = metodo_secante(g, 0, 1)

if raiz_sec:
    print(f"Raiz encontrada via Secante: {raiz_sec:.6f}")
else:
    print("O método não convergiu.")
```


### Exemplo 3: Newton-Raphson com plot

```python
import matplotlib.pyplot as plt
from CB2325NumericaG07.raizes import metodo_bissecao

# Função: f(x) = 10x^3 - 200x + 432
f = lambda x: 10*x**3 - 200*x + 432

# Busca a raiz no intervalo
raiz = metodo_newton_raphson(função, tol=1e-6, plotar=True)

print(f"Raiz encontrada: {raiz:.6f}")
# Saída esperada: aprox. −5.305019
```

### Exemplo 4: grid search
```python
from CB2325NumericaG07.raizes import grid_search


def grid_search(func,a,b,n= 1000):
    intervals = []
    vals = np.linspace(a,b,n)
    for idx in range(1,len(vals)):
        if func(vals[idx-1])*func(vals[idx]) <= 0:
            intervals.append((vals[idx-1],vals[idx]))

    return intervals


import numpy as np
f = lambda x : np.sin(x)

print(f'Os intervalos encontrados para calcular as raizes são : {grid_search(f,0,10)}')


```
