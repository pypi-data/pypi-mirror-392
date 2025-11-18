"""Módulo responsável pela geração e exibição das cartelas"""


def geraCartelas():

    cartelas = [[], [], [], [], [], []]

    for i in range(1, 64):
        prox = i

        for cartela in cartelas:
            if prox % 2 == 1:
                cartela.append(i)

            prox = prox // 2

    return cartelas

def exibeCartela(cartela, n):

    print(f"\nCartela {n+1}")

    for pos, n in enumerate(cartela):
        print(str(n).rjust(2), end=" ")

        if (pos + 1) % 8 == 0:
            print()