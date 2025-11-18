# `integracao.py` - Módulo de Integração Numérica

Este módulo fornece ferramentas para calcular integrais definidas de funções usando métodos numéricos. É capaz de lidar tanto com funções Python padrão quanto com expressões simbólicas da biblioteca SymPy.

## Dependências

Este módulo requer as seguintes bibliotecas Python para sua funcionalidade completa:

* **NumPy**: Para operações numéricas e arrays.
* **SymPy**: Para manipulação de expressões simbólicas.
* **Matplotlib**: Para a visualização gráfica (opcional).

## Funções

### `integral_trapezio`

Calcula a integral definida de uma função usando o método do trapézio (regra trapezoidal composta).

#### Parâmetros

* **`function`** (callable ou `sp.Expr`): A função a ser integrada.
    * Pode ser uma função Python padrão (ex: `lambda x: x**2`).
    * Pode ser uma expressão ou Lambda do SymPy (ex: `sp.sin(x)`), que será convertida automaticamente para uma função numérica.
* **`a`** (float): O limite inferior da integração.
* **`b`** (float): O limite superior da integração.
* **`n`** (int): O número de subintervalos (trapézios) a serem usados. Deve ser maior ou igual a 1.
* **`plotar`** (bool, opcional): Se `True`, exibe um gráfico usando `matplotlib` que visualiza a função e os trapézios usados na aproximação. O padrão é `False`.

#### Retorna

* **`float`**: O valor aproximado da integral definida.

#### Fórmula Matemática

A Regra do Trapézio Composta é definida como:

$$
\int_{a}^{b} f(x) \,dx \approx \frac{h}{2} \left[ f(x_0) + 2\sum_{i=1}^{n-1} f(x_i) + f(x_n) \right]
$$

Onde:  
* $h = (b - a) / n$  
* $x_i = a + i \cdot h$

---

## Exemplos de Uso

Abaixo estão exemplos de como usar a função `integral_trapezio`.

```python
import math
import sympy as sp
from integracao import integral_trapezio # Supondo que o arquivo se chame integracao.py

# Simplificações do SymPy
pi, sin, cos = sp.pi, sp.sin, sp.cos
x = sp.symbols('x')
```

### Exemplo 1: Função Python Padrão (lambda)

Integrando $f(x) = x^2$ de 0 a 1, que analiticamente é $1/3$.

```python
f_lambda = lambda x: x**2
resultado = integral_trapezio(f_lambda, a=0, b=1, n=100)
print(f"Integral de x^2 de 0 a 1 (n=100): {resultado}")
# Saída esperada: ~0.33335
```

### Exemplo 2: Expressão SymPy

Integrando $f(x) = \sin(x)$ de 0 a $\pi$, que analiticamente é 2. A função lida automaticamente com a expressão `sp.sin(x)`.

```python
f_sympy = sin(x)
resultado_sym = integral_trapezio(f_sympy, a=0, b=pi, n=50)
print(f"Integral de sin(x) de 0 a pi (n=50): {resultado_sym}")
# Saída esperada: ~1.9993
```

### Exemplo 3: Usando a Visualização Gráfica

Calculando a integral de uma função mais complexa e ativando o parâmetro `plotar`.

```python
f_complexa = lambda x: (x**2) * math.sin(x)

print("Calculando e plotando a integral de x^2 * sin(x)...")

# A chamada da função irá exibir um gráfico
resultado_plot = integral_trapezio(f_complexa, a=0, b=10, n=20, plotar=True)

print(f"Resultado da integral (n=20): {resultado_plot}")
```


### `integral_de_montecarlo`

Calcula a integral definida de uma função usando o método de monte carlo.

#### Parâmetros

* **`function`** (callable): Função que será integrada.
* **`a`** (float): O limite inferior da integração.
* **`b`** (float): O limite superior da integração.
* **`c`** (float): Limite superior em y da integral.
* **`d`** (float): Limite inferior em y da integral.
* **`qte`** (int): Quantidade de pontos que serão gerados para calcular a integral.
* **`plot`** (bool, opcional): Se `True`, exibe um gráfico usando `matplotlib` que visualiza os pontos usados e a função integrada. O padrão é `False`.

#### Retorna

* **`float`**: O valor aproximado da integral definida.

#### Fórmula Matemática

A integral de montecarlo consiste em gerar pontos aleatoriamente em um quadrado, e calcular a proporção entre os valores que estão 'dentro' da área calculada pela integral. 


---

## Exemplos de Uso

Abaixo estão exemplos de como usar a função `integral_de_montecarlo`.

```python
import math
import sympy as sp
from integracao import integral_trapezio # Supondo que o arquivo se chame integracao.py

# Simplificações do SymPy
pi, sin, cos = sp.pi, sp.sin, sp.cos
```

### Exemplo 1: Função Python Padrão (lambda)

Integrando $f(x) = x^2$ de 0 a 1, que analiticamente é $1/3$.

```python

f_lambda = lambda x: x**2

resultado = integral_de_montecarlo(f_lambda, a=0, b=1,qte=100)
print(f"Integral de x^2 de 0 a 1 (qte=100): {resultado}")
# Saída esperada: ~0.33335
```

### Exemplo 2: Expressão SymPy

Integrando $f(x) = \sin(x)$ de 0 a $\pi$, que analiticamente é 2.

```python
f_lamda = lambda x : sin(x)
resultado = integral_de_montecarlo(f_lamda, a=0, b=pi, qte=50)
print(f"Integral de sin(x) de 0 a pi (qte=50): {resultado}")
# Saída esperada: ~1.9993
```

### Exemplo 3: Usando a Visualização Gráfica

Calculando a integral de uma função mais complexa e ativando o parâmetro `plotar`.

```python
f_complexa = lambda x: (x**2) * math.sin(x)

print("Calculando e plotando a integral de x^2 * sin(x)...")

# A chamada da função irá exibir um gráfico
resultado_plot = integral_de_montecarlo(f_complexa, a=0, b=10, qte=20, plot=True)

print(f"Resultado da integral (qte=20): {resultado_plot}")
```

### `integral_simpson38`

Calcula a integral definida de uma função utilizando a Regra de Simpson 3/8 — um método numérico baseado em interpolação cúbica.
É mais precisa que a Regra dos Trapézios e que a Simpson 1/3 em algumas situações.

#### Parâmetros

* **`function`** (callable):Função Python que recebe um valor x e retorna f(x).
* **`a`** (float): Limite inferior da integração.
* **`b`** (float): Limite superior da integração.
* **`n`** (int):
    * Número de subintervalos.
    * Deve ser múltiplo de 3, pois cada bloco da fórmula usa 3 subintervalos.
**`plotar`** (bool, opcional): Se True, exibe um gráfico ilustrando a interpolação cúbica usada pelo método.

#### Retorna

* **`float`**: valor aproximado da integral definida.

#### Fórmula Matemática

A Regra de Simpson 3/8 composta é dada por:

$$
\int_{a}^{b} f(x)\ dx \approx \frac{3h}{8}\left[f(x_0)+3 \sum_{\substack{i=1 \\ i \not\equiv 0 \pmod{3}}}^{n-1} f(x_i)+2 \sum_{\substack{i=3 \\ i \equiv 0\pmod{3}}}^{\,n-3}f(x_i)+f(x_n)\right]
$$

Onde:

* $h = \frac{b-a}{n}$
* $x_i = a + ih.$

---

## Exemplos de Uso

## Exemplo 1 — Função Python (lambda)

```python

f = lambda x: np.sin(x)
resultado = integral_simpson38(f, 0, np.pi, n=99)
print(resultado)
```

## Exemplo 2 — Plotando

```python

f = lambda x: np.cos(x) * x
resultado = integral_simpson38(f, 0, 3, n=99, plotar=True)
```

### `integral_boole`

Calcula a integral definida de uma função usando a Regra de Boole, também chamada Newton–Cotes de 4ª ordem.
Ela utiliza 5 pontos igualmente espaçados e um polinômio de grau 4 para aproximar a integral em cada bloco.

#### Parâmetros

* **`function`** (callable): Função a ser integrada.
* **`a`** (float): Limite inferior.
* **`b`** (float): Limite superior.
* **`n`** (int): Número de subintervalos.
*   * Deve ser múltiplo de 4, pois cada bloco da fórmula usa 4 subintervalos e 5 pontos.
* **`plotar`** (bool): Se True, exibe gráfico da função e dos pontos utilizados.

#### Retorna

* **`float`**: aproximação da integral.

#### Fórmula Matemática

$$
\int_{a}^{b} f(x)\, dx \approx \frac{2h}{45}\left[7f(x_0) + 32f(x_1) + 12f(x_2) + 32f(x_3)+ 7f(x_4)\right]
$$

Aplicada repetidamente em intervalos de 4 subintervalos.

$h = \frac{b - a}{4}.$

## Exemplos de Uso

```python

f = lambda x: np.sin(x)
resultado = integral_boole(f, 0, np.pi, n=8)
print(resultado)
```

### `integral_gauss_legendre`

Calcula a integral definida usando o método de Quadratura de Gauss–Legendre, um dos mais precisos métodos de integração para funções suaves.
Ele utiliza os zeros dos polinômios de Legendre como pontos de amostragem e pesos ideais que minimizam o erro.

#### Parâmetros

* **`function`** (callable): Função a integrar.
* **`a, b`** (float): Limites da integral.
* **`n`** (int, opcional):
*   * Número de pontos da quadratura.
*   * O método é exato para polinômios até grau 2n−1.
*   * Valor padrão: 3.
* **`plotar`** (bool): Se True, exibe gráfico com a função e os nós usados.

#### Retorna

* **`float`** – Valor aproximado da integral.

#### Fórmula Matemática

$$
\int_{a}^{b} f(x)\ dx\approx\frac{b - a}{2}\sum_{i = 1}^{n}w_i f\Big(\frac{b - a}{2}\ x_i+\frac{a + b}{2}\Big).
$$

Onde:

$x_i$: nós de Gauss (zeros do polinômio de Legendre)
$w_i$: pesos correspondentes

## Exemplos de Uso

```python

f = lambda x: np.sin(x)
resultado = integral_gauss_legendre(f, 0, np.pi, n=3)
print(resultado)
```