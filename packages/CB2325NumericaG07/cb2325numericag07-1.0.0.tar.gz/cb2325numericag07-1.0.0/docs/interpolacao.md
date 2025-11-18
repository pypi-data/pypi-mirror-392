Adicionar documentação
# `intepolacao.py` - Módulo de Interpolação 

Esse modulo fornece ferramentas para a interpolação de pontos.

## Dependências

Este módulo requer as seguintes bibliotecas Python para sua funcionalidade completa:

* **NumPy**: Para operações numéricas e arrays.
* **SymPy**: Para manipulação de expressões simbólicas.
* **Matplotlib**: Para a visualização gráfica (opcional).


## Funções

## `diff_numerica`

Calcula as derivadas numéricas de uma sequencia de pontos.

#### Parâmetros

* **`x`** (`list`): lista das coordenadas x dos pontos.
* **`y`** (`list`): lista das coordenadas y dos pontos.

#### Retorna

* **`list`**: lista das derivadas em cada um dos pontos.


## `_function_definer`

Retorna uma função que relaciona os pontos de uma lista x com uma lista y.

#### Parâmetros

* **`Lista_x`** (`list`) : Lista x que será o dominio da função.
* **`Lista_x`** (`list`) : Lista y que será a imagem da função.
* **`exception`** : Valor, ou qualquer outra coisa que a função retornará se aplicada a um valor fora do dominio (Lista x).

#### Retorna

* **`function`**: Função que relaciona os valores do dominio com os respectivos valores da imagem.



## `_duplicate`

Retorna uma lista com os valores duplicados da forma [1,2,3] -> [1,1,2,2,3,3].

#### Parâmetros

* **`Lista`** (`list`) : Lista x que será duplicada.

#### Retorna

* **`list`**: Lista duplicada.


## `__hermite_ddfunc`

Calcula os valores das diferenças divididas de uma função considerando pontos duplicados como derivada.

#### Parâmetros

* **`Point_list`** (`list`) : Lista das coordenadas x dos pontos que serão interpolados,(Funciona para lista de pontos normais, mas para a hermite mas especificamente é necessário que a lista seja duplicada da forma [1,2,3] -> [1,1,2,2,3,3]).
* **`derivada`** (`function`) : Função que dado um dos valores das coordenadas x dos pontos de Point_list, retorne a derivada no ponto.
* **`func`** (`function`): Função que dado um valor das coordenadas x, retorna o respectivo valor da coordenada y.

#### Retorna

* **`list`**: Retorna uma lista com o os coeficientes necessários para a interpolação de hermite em ordem de uso .


## `interpolacao_de_hermite`

Calcula a função da interpolação de hermite.

#### Parâmetros

* **`x`** (`list`) : Lista das coordenadas x dos pontos escolhidos para a interpolação.
* **`y`** (`list`) : Lista das coordenadas y dos pontos escolhidos para a interpolação.
* **`plot`** (`bool`): Determina se o plot deve acontecer ou não.
* **`grid`** (`bool`): Determina se o plot deve ter grid ou não.

#### Retorna

* **`function`**: Retorna uma função que calcula os valores para a função interpolada.

#### Matemática

A interpolação de hermite funciona com as diferenças divididas da forma:

$$
H(x) = f[x_0] + f[x_0,x_0](x - x_0) + f[x_0,x_0,x_1](x - x_0)^2 + f[x_0,x_0,x_1,x_1](x - x_0)^2 (x - x_1) ...
$$




## `_newton_ddfunc`

Calcula os valores das diferenças divididas de uma função sem valores repetidos.

#### Parâmetros

* **`Point_list`** (`list`) : Lista das coordenadas x dos pontos que serão interpolados.
* **`func`** (`function`): Função que dado um valor das coordenadas x, retorna o respectivo valor da coordenada y.

#### Retorna

* **`list`**: Retorna uma lista com o os coeficientes necessários para a interpolação de newton em ordem de uso.



## `interpolacao_de_newton`


Calcula a função da interpolação de hermite.

#### Parâmetros

* **`x`** (`list`) : Lista das coordenadas x dos pontos escolhidos para a interpolação.
* **`y`** (`list`) : Lista das coordenadas y dos pontos escolhidos para a interpolação.
* **`plot`** (`bool`): Determina se o plot deve acontecer ou não.
* **`grid`** (`bool`): Determina se o plot deve ter grid ou não.

#### Retorna

* **`function`**: Retorna uma função que calcula os valores para a função interpolada.

#### Matemática

A interpolação de newton funciona com as diferenças divididas da forma:

$$
H(x) = f[x_0] + f[x_0,x_1](x - x_0) + f[x_0,x_1,x_2](x - x_0)(x - x_1) + ...
$$




Este módulo fornece ferramentas para calcular o **polinômio interpolador** para um conjunto de pontos, utilizando os métodos de **Lagrange** e da **Matriz de Vandermonde**.

## Dependências

Este módulo requer as seguintes bibliotecas Python para sua funcionalidade completa:

* **NumPy (`np`)**: Para operações numéricas eficientes e manipulação de arrays (e.g., construção da Matriz de Vandermonde e preparação de dados para plotagem).
* **SymPy (`sp`)**: Para manipulação de **expressões simbólicas** e simplificação dos polinômios.
* **Matplotlib (`plt`)**: Para a visualização gráfica do polinômio e dos pontos originais (opcional, requer `plotar=True`).


## Funções

### `interpolacao_polinomial` (Método de Lagrange)

Calcula o Polinômio Interpolador de **Lagrange** para um conjunto de pontos $\left(x_i, f(x_i)\right)$ dados, construindo-o pela soma dos Polinômios Construtores $L_k(x)$.

#### Parâmetros

* **`tupla_de_pontos`** (`list of tuple`): Lista contendo os pontos de interpolação na forma `[(x0, f(x0)), (x1, f(x1)), ...]`. Os valores de $x$ devem ser distintos.
* **`plotar`** (`bool`, *opcional*): Se `True`, gera e exibe um gráfico do polinômio interpolador e dos pontos originais usando **Matplotlib**. Padrão é `False`.

#### Retorna

* **`sympy.Expr`** (se bem-sucedido): A expressão simbólica do polinômio de Lagrange simplificado, na forma padrão (e.g., $a_n x^n + \dots + a_0$).
* **`str`** (se erro): Uma mensagem de erro se a lista de pontos estiver vazia.

#### Matemática

O Polinômio Interpolador de Lagrange, $P(x)$, é dado por:

$$
P(x) = \sum_{k=0}^{n-1} f(x_k) \cdot L_k(x)
$$

Onde $L_k(x)$ são os **Polinômios Construtores de Lagrange**:

$$
L_k(x) = \prod_{\substack{i=0 \\ i \neq k}}^{n-1} \frac{x - x_i}{x_k - x_i}
$$



### `interp_vand` (Método da Matriz de Vandermonde)

Calcula o Polinômio Interpolador através da solução do **Sistema Linear** $V \cdot \mathbf{a} = \mathbf{Y}$, onde $V$ é a **Matriz de Vandermonde**, $\mathbf{a}$ são os coeficientes do polinômio e $\mathbf{Y}$ são os valores de $f(x_i)$.

#### Parâmetros

* **`tupla_de_pontos`** (`list of tuple`): Lista contendo os pontos de interpolação na forma `[(x0, f(x0)), (x1, f(x1)), ...]`. Os valores de $x$ devem ser distintos.
* **`plotar`** (`bool`, *opcional*): Se `True`, gera e exibe um gráfico do polinômio interpolador e dos pontos originais usando **Matplotlib**. Padrão é `False`.

#### Retorna

* **`sympy.Expr`** (se bem-sucedido): A expressão simbólica do polinômio na forma padrão $P(x) = a_0 + a_1 x + \dots + a_{n-1} x^{n-1}$.
* **`str`** (se erro): Uma mensagem de erro se a lista de pontos estiver vazia ou se a matriz de Vandermonde for singular (e.g., devido a pontos $x$ duplicados).

#### Matemática

O polinômio é buscado na forma:
$$
P(x) = a_0 + a_1 x + a_2 x^2 + \dots + a_{n-1} x^{n-1}
$$

A condição $P(x_i) = f(x_i)$ para todos os $n$ pontos leva ao sistema linear:

$$
\begin{pmatrix}
1 & x_0 & x_0^2 & \dots & x_0^{n-1} \\
1 & x_1 & x_1^2 & \dots & x_1^{n-1} \\
\vdots & \vdots & \vdots & \ddots & \vdots \\
1 & x_{n-1} & x_{n-1}^2 & \dots & x_{n-1}^{n-1}
\end{pmatrix}
\begin{pmatrix}
a_0 \\
a_1 \\
\vdots \\
a_{n-1}
\end{pmatrix}
=
\begin{pmatrix}
f(x_0) \\
f(x_1) \\
\vdots \\
f(x_{n-1})
\end{pmatrix}
$$

A primeira matriz é a **Matriz de Vandermonde** ($V$). A solução deste sistema, o vetor $\mathbf{a} = \left(a_0, a_1, \dots, a_{n-1}\right)^T$, fornece os coeficientes do polinômio.


### `interpolacao_linear_por_partes`

Constrói a **interpolação linear por partes** a partir de pontos dados, produzindo um polinômio linear em cada intervalo $[x_i, x_{i+1}]$.

#### Parâmetros

* **`x_vals`** (`list`): Lista contendo os valores de \(x\) dos pontos.
* **`y_vals`** (`list`): Lista contendo os valores de \(y\) correspondentes.
  Ambas as listas devem ter o mesmo comprimento.

* **`plotar`** (`bool`, opcional):  
  Se `True`, plota os pontos originais e os segmentos lineares.  
  Padrão é `False`.

* **`x_test`** (`float` | `int` | `None`, opcional):  
  Valor onde se deseja avaliar a interpolação.  
  Se fornecido, a função retorna também o valor interpolado.

#### Retorna

* **`list[sympy.Expr]`**: Lista contendo os polinômios lineares $P_i(x)$ de cada intervalo.
* **`tuple`** (se `x_test` for fornecido): `(lista_de_polinomios, valor_interpolado)`.
* **`str`**: Mensagem de erro caso `x_test` esteja fora do domínio.

#### Matemática

A interpolação linear por partes toma pontos:

$$
(x_0, y_0), (x_1, y_1), \dots, (x_{n-1}, y_{n-1})
$$

e constrói um polinômio linear em cada subintervalo.

O polinômio no intervalo $\[x_i, x_{i+1}]\$ é:

$$
P_i(x) = y_i + \frac{y_{i+1} - y_i}{x_{i+1} - x_i}(x - x_i)
$$

A função completa é dada por:

$$
P(x) =
\begin{cases}
P_0(x), & x_0 \le x \le x_1 \\
P_1(x), & x_1 \le x \le x_2 \\
\vdots \\
P_{n-2}(x), & x_{n-2} \le x \le x_{n-1}
\end{cases}
$$

Onde cada $P_i(x)$ é um polinômio de grau $1$. A função é contínua mas não necessariamente diferenciável nos pontos $x_i$.


