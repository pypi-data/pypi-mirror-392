# `aproximacao.py` - Módulo de Aproximação

Este módulo fornece ferramentas para calcular funções de aproximação de pontos.

## Dependências

Este módulo requer as seguintes bibliotecas Python para sua funcionalidade completa:

* **NumPy**: Para operações numéricas e arrays.
* **SymPy**: Para manipulação de expressões simbólicas.
* **Matplotlib**: Para a visualização gráfica (opcional).

## Funções

### `_plotar_grafico`

Plota o gráfico com os dados fornecidos pelo usuário e a função aproximadora encontrada.

É chamada internamente por outras funções de `aproximacao.py`. 

#### Parâmetros

* **`valores_x`** (ArrayLike): A variável independente (lista ou array NumPy de valores).
* **`valores_y`** (ArrayLike): A variável dependente (lista ou array NumPy de valores).
* **`func_sym`** (sp.Expr): Função simbólica da aproximação que se busca visualizar.
* **`titulo`** (str): Título do gráfico.
* **`qtd_pontos`** (int, opcional): Define a quantidade de pontos exibidos no gráfico da função de ajuste. O padrão é 200.

---

### `ajuste_linear`

Calcula os coeficientes de um ajuste linear (modelo $y = ax + b$) para um conjunto de dados (valores_x, valores_y) usando o Método dos Mínimos Quadrados (MMQ).

#### Parâmetros

* **`valores_x`** (ArrayLike): A variável independente (lista ou array NumPy de valores).
* **`valores_y`** (ArrayLike): A variável dependente (lista ou array NumPy de valores).
* **`plt_grafico`** (bool, opcional): Se `True`, exibe um gráfico do ajuste usando `matplotlib`. O padrão é `False`.
* **`expr`** (bool, opcional): Se `True`, imprime a expressão matemática encontrada. O padrão é `False`.

#### Retorna

* **`np.ndarray`**: Um array NumPy contendo os coeficientes `[a, b]` do modelo.

#### Fórmula Matemática

O ajuste linear $y = ax + b$ é encontrado minimizando a soma dos quadrados dos resíduos. Os coeficientes são calculados como:

$$
a = \frac{\sum_{i=1}^{n} (x_i - \bar{x})(y_i - \bar{y})}{\sum_{i=1}^{n} (x_i - \bar{x})^2} = \frac{Cov(valores\_x, valores\_y)}{Var(valores\_x)}
$$
$$
b = \bar{y} - a \bar{x}
$$

Onde:
* $n$ = número de pontos.
* $\bar{x}$ = média dos valores de valores_x.
* $\bar{y}$ = média dos valores de valores_y.

---

### `ajuste_polinomial`

Calcula os coeficientes de um ajuste polinomial (modelo $y = c_{0} + c_{1}x + ... + c_{n}x^{n}$) para um conjunto de dados (valores_x, valores_y) usando o Método dos Mínimos Quadrados (MMQ).

#### Parâmetros

* **`valores_x`** (ArrayLike): A variável independente (lista ou array NumPy de valores).
* **`valores_y`** (ArrayLike): A variável dependente (lista ou array NumPy de valores).
* **`grau_pol`** (int): Grau do polinômio ao qual os dados serão ajustados.
* **`plt_grafico`** (bool, opcional): Se `True`, exibe um gráfico do ajuste usando `matplotlib`. O padrão é `False`.
* **`expr`** (bool, opcional): Se `True`, imprime a expressão matemática encontrada. O padrão é `False`.

#### Retorna

* **`np.ndarray`**: Um array NumPy contendo os coeficientes do modelo em ordem crescente referente ao grau da variável a que estão associados, ou seja: `[c0, c1, ..., cn]`.

#### Método Utilizado

O ajuste polinomial $y = c_{0} + c_{1}x + ... + c_{n}x^{n}$ é encontrado a partir de uma decomposição SVD, a qual é implementada pelo **`numpy.linalg.lstsq`**. 

Esse método promove maior estabilidade quanto a erros numéricos e ao mal condicionamento de matrizes, especialmente em comparação com a fórmula dos mínimos quadrados normais.

---

### `ajuste_exponencial`

Calcula os coeficientes de um ajuste exponencial (modelo $y = b \cdot e^{ax}$) para um conjunto de dados (valores_x, valores_y). O método lineariza o modelo aplicando o logaritmo natural.

#### Parâmetros

* **`valores_x`** (ArrayLike): A variável independente.
* **`valores_y`** (ArrayLike): A variável dependente. **Requer que todos os valores de valores_y sejam positivos.**
* **`plt_grafico`** (bool, opcional): Se `True`, exibe um gráfico do ajuste. O padrão é `False`.
* **`expr`** (bool, opcional): Se `True`, imprime a expressão matemática encontrada. O padrão é `False`.

#### Retorna

* **`np.ndarray`**: Um array NumPy contendo os coeficientes `[a, b]` do modelo.

#### Fórmula Matemática

O modelo $y = b \cdot e^{ax}$ é linearizado tomando o logaritmo natural em ambos os lados:
$$
\ln(y) = \ln(b) + ax
$$
Definindo $Y' = \ln(y)$ e $b' = \ln(b)$, o problema é reduzido a um ajuste linear $Y' = b' + ax$. Os coeficientes $a$ e $b'$ são encontrados por MMQ.

O coeficiente $b$ é então recuperado por:
$$
b = e^{b'}
$$

Onde:
* $a$ e $b'$ são os coeficientes do ajuste linear $Y' = ax + b'$.

---

### `ajuste_logaritmo`

Calcula os coeficientes de um ajuste logarítmico (modelo $y = a + b \cdot \ln(x)$) para um conjunto de dados (valores_x, valores_y). O método lineariza o modelo usando $\ln(x)$ como a nova variável independente.

#### Parâmetros

* **`valores_x`** (ArrayLike): A variável independente. **Requer que todos os valores de valores_x sejam positivos.**
* **`valores_y`** (ArrayLike): A variável dependente.
* **`plt_grafico`** (bool, opcional): Se `True`, exibe um gráfico do ajuste. O padrão é `False`.
* **`expr`** (bool, opcional): Se `True`, imprime a expressão matemática encontrada. O padrão é `False`.

#### Retorna

* **`np.ndarray`**: Um array NumPy contendo os coeficientes `[a, b]` do modelo.

#### Fórmula Matemática

O modelo $y = a + b \cdot \ln(x)$ é linearizado pela substituição $X' = \ln(x)$.
O problema é reduzido a um ajuste linear:
$$
y = a + bX'
$$
Os coeficientes $a$ e $b$ são então encontrados diretamente pelo Método dos Mínimos Quadrados.

Onde:
* $a$ e $b$ são os coeficientes do ajuste linear $y = a + bX'$.

---

### `ajuste_senoidal`

Calcula os coeficientes de um ajuste senoidal (modelo $y = A \cdot \sin(Bx + C) + D$) para um conjunto de dados (valores_x, valores_y). O método lineariza o modelo a partir da estimativa inicial do período fornecida pelo usuário.

#### Parâmetros

* **`valores_x`** (ArrayLike): A variável independente.
* **`valores_y`** (ArrayLike): A variável dependente.
* **`T_aprox`** (float): O período aproximado.
* **`plt_grafico`** (bool, opcional): Se `True`, exibe um gráfico do ajuste. O padrão é `False`.
* **`expr`** (bool, opcional): Se `True`, imprime a expressão matemática encontrada. O padrão é `False`.

#### Retorna

* **`np.ndarray`**: Um array NumPy contendo os coeficientes `[A, B, C, D]` do modelo.

#### Método Utilizado

O modelo $y = A \cdot \sin(Bx + C) + D$ é linearizado tal que $y = a \cdot \sin(Bx) + b \cdot \cos(Bx) + d$.

Onde:
* $a = A \cdot \cos(C)$
* $b = A \cdot \sin(C)$
* $d = D$

O problema é reduzido, então, à obtenção dos coeficientes $a$, $b$ e $d$.

Para isso, inicialmente encontra-se uma frequência $B$ adequada. Isso é feito ao avaliar os erros quadráticos obtidos para valores de frequência em torno da frequência inicial $B_{0}$ (esta é captada pela aproximação do período inserida pelo usuário como parâmetro da função, de modo que $B_{0} = \frac{2\pi}{T_{aprox}}$).

Após isso, $a$, $b$ e $d$ são estimados pelo Método dos Mínimos Quadrados, o qual é abordado a partir de uma decomposição SVD implementada pelo **`numpy.linalg.lstsq`**. 

O programa, então, calcula:
* $A = \sqrt{a^2 + b^2}$
* $C = \operatorname{arctan2}(b,a)$

---

### `ajuste_multiplo`

Calcula os coeficientes de um ajuste múltiplo (modelo $y = c_{0} + c_{1}x_{1} + ... + c_{n}x_{n}$) para um conjunto de dados (valores_var, valores_y). O método lineariza o modelo usando o Método dos Mínimos Quadrados (MMQ).

#### Parâmetros

* **`valores_var`** (ArrayLike): As variáveis independentes (sendo cada linha referente às amostras de cada variável).
* **`valores_y`** (ArrayLike): A variável dependente.
* **`incluir_intercepto`** (bool, opcional): Se `True`, busca também um intercepto $c_{0}$ nos cálculos. O padrão é `False`.
* **`expr`** (bool, opcional): Se `True`, imprime a expressão matemática encontrada. O padrão é `False`.

#### Retorna

* **`np.ndarray`**: Um array NumPy contendo os coeficientes do modelo. 

    Caso **`incluir_intercepto`**, o termo $c_{0}$ ocupa a primeira posição no array, seguido dos outros coeficientes atrelados às variáveis na ordem em que estas foram inseridas em **`valores_var`**. Do contrário, apenas os coeficientes atrelados às variáveis são incluídos.

#### Método Utilizado

O ajuste múltiplo $y = c_{0} + c_{1}x_{1} + ... + c_{n}x_{n}$ é encontrado a partir de uma decomposição SVD, a qual é implementada pelo **`numpy.linalg.lstsq`**.

O modelo adotado também busca tratar os casos de mal condicionamento dos dados inseridos, uma vez que pode ser impactado por casos de colinearidade.

---

### `avaliar_ajuste`

Avalia a qualidade de um modelo de ajuste (previamente calculado) usando um ou mais critérios estatísticos.

#### Parâmetros

* **`valores_x`** (ArrayLike): Lista de valores da variável independente usados no ajuste.
* **`valores_y`** (ArrayLike): Lista de valores da variável dependente usados no ajuste.
* **`criterio`** (str): O critério de avaliação desejado. Opções: `"R2"`, `"R2A"`, `"AIC"`, `"AICc"`, `"BIC"`, ou `"all"` (para retornar todos).
* **`modelo`** (str): O nome do modelo que gerou os coeficientes. Opções: `"linear"`, `"polinomial"`, `"exponencial"`, `"logaritmo"`, `"senoidal"`.
* **`coeficientes`** (tuple | np.ndarray): Os coeficientes retornados pela função de ajuste correspondente.

#### Retorna

* **`float`** | **`tuple`**: O valor do critério solicitado (se `criterio` != `"all"`) ou uma tupla contendo (R2, R2A, AIC, AICc, BIC) (se `criterio` == `"all"`).

#### Fórmula Matemática

As métricas são baseadas na Soma dos Quadrados dos Resíduos (RSS) e na Soma dos Quadrados Total (RST).

$$
RSS = \sum_{i=1}^{n} (y_i - \hat{y}_i)^2 \quad \text{(Soma dos Quadrados dos Resíduos)}
$$
$$
RST = \sum_{i=1}^{n} (y_i - \bar{y})^2 \quad \text{(Soma dos Quadrados Total)}
$$

**Critérios:**
* **R² (Coef. de Determinação):** $R^2 = 1 - \frac{RSS}{RST}$
* **R² Ajustado:** $R^2_{A} = 1 - \frac{(1 - R^2)(n - 1)}{n - k}$
* **AIC (Critério de Akaike):** $AIC = n \cdot \ln\left(\frac{RSS}{n}\right) + 2k$
* **BIC (Critério Bayesiano):** $BIC = n \cdot \ln\left(\frac{RSS}{n}\right) + k \cdot \ln(n)$
* **AICc (AIC Corrigido):** $AICc = AIC + \frac{2k(k+1)}{n - k - 1}$

Onde:
* $n$ = número de amostras (pontos).
* $k$ = número de coeficientes (parâmetros) do modelo, incluindo o intercepto.
* $y_i$ = valor observado; $\hat{y}_i$ = valor previsto pelo modelo; $\bar{y}$ = média dos valores observados.

---

### `melhor_ajuste`

Sugere qual modelo de ajuste (linear ou polinomial de grau 2 a 10) pode ser o mais adequado a partir de um critério estatístico selecionado pelo usuário (a saber, $R^2$, $R^2$ ajustado, $AIC$, $AICc$ ou $BIC$).

#### Parâmetros

* **`valores_x`** (ArrayLike): Lista de valores da variável independente usados no ajuste.
* **`valores_y`** (ArrayLike): Lista de valores da variável dependente usados no ajuste.
* **`criterio`** (str): O critério de avaliação desejado para a sugestão. Opções: `"R2"`, `"R2A"` ($R^2$ ajustado), `"AIC"`, `"AICc"` ou `"BIC"`.
* **`exibir_todos`** (bool, opcional): Se `True`, imprime os valores dos outros critérios do modelo sugerido. O padrão é `False`.
* **`plt_grafico`** (bool, opcional): Se `True`, exibe o gráfico do ajuste sugerido. O padrão é `False`.
* **`expr`** (bool, opcional): Se `True`, imprime a expressão matemática do ajuste sugerido. O padrão é `False`.


#### Retorna

* **`str`**: O nome do modelo sugerido (`linear` ou `"polinomial grau i"`).
* **`dict`**: Dicionário com as principais informações do modelo sugerido (`params` (parâmetros), `SSE` (Soma dos Quadrados dos Erros), `R2`, `R2A`, `AIC`, `AICc`, `BIC`)

#### Método Utilizado

O programa obtém os coeficientes de regressão de cada modelo de ajuste (ajuste linear e polinomial de grau 2 a 10) através da função `ajuste` aplicada aos dados.

Além disso, o programa calcula a Soma dos Quadrados dos Erros (SSE) de cada modelo por meio da seguinte fórmula:

$$
SSE = \sum_{i = 1}^{n} (y_{i} - f(x_{i}))^2
$$

, em que $y_{i}$ é o i-ésimo valor da variável dependente inserida pelo usuário e $f(x_{i})$ corresponde ao valor da função de aproximação para o i-ésimo valor da variável independente.

Em seguida, ele obtém os valores dos critérios R2, R2A, AIC, AICc e BIC para cada modelo de ajuste a partir da função `avaliar_ajuste`. 

Por fim, ele seleciona o modelo que obteve o melhor valor para o critério escolhido pelo usuário. Mais especificamente, no caso do R2 e do R2A, busca-se o maior, e no caso do AIC, AICc e BIC, busca-se o menor.

---