def erro_absoluto(valor_real,valor_aprox):
    """
    Calcula o erro absoluto entre o valor real definido e o valor
      aproximado.

    Parâmetros:
        valor_real(float): Valor considerado verdadeiro.
        valor_aprox(float): Valor aproximado

    Retorna:
        float: O erro absoluto, dado por |valor_real - valor_aprox|.
    """
    return abs(valor_real-valor_aprox)

def erro_relativo(valor_real,valor_aprox):
    """
    Calcula o erro relativo entre o valor real e o valor aproximado.

    Parâmetros:
        valor_real(float): Valor considerado verdadeiro.
        valor_aprox(float): Valor aproximado.

    Retorna:
        float: O erro relativo, dado por 
        |valor_real - valor_aprox| / |valor_real|.
    """
    if valor_real == 0:
        if valor_aprox == 0:
            return 0.0 #para 0/0
        else:
            return float('inf') #erro infinito se valor_real é 0 e valor_aprox não é 0

    return abs(valor_real-valor_aprox)/abs(valor_real)

if __name__ == '__main__':
    print(erro_absoluto.__doc__)
    print(erro_relativo.__doc__)