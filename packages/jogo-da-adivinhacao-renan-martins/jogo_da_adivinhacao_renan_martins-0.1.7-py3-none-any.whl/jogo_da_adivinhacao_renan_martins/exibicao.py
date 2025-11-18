"""Módulo responsável pela interface e mensagens do jogo"""
from config import VERSION

def exibeMensagemInicial():
    print("*" * 63)
    print("*", f"Jogo da Adivinhação | Versão {VERSION}".center(60), end="*")
    print(
        "\n*",
        "Pense em um inteiro de 1 a 63 e não conte pra ninguém!".center(60),
        end="*",
    )
    print(
        "\n*",
        "Em seguida, tecle ENTER para continuar... e boa sorte!".center(60),
        end="*",
    )
    print("\n*", "*".rjust(61))
    print("*" * 63)
    input("\nPensou? tecle ENTER...")

def exibeValorEscolhido(valor):
    print("\n" + "*" * 63)
    print("*" + " " * 61 + "*")
    print("*" + f"ATENÇÃO! O valor escolhido foi: {valor}".center(61) + "*")
    print("*" + " " * 61 + "*")
    print("*" * 63)

def exibeMensagemFinal():
    print("*" * 63)
    print("*", f"Jogo da Adivinhação | Versão {VERSION}".center(60), end="*")
    print(
        "\n*",
        "Por Renan Martins".center(60),
        end="*",
    )
    print(
        "\n*",
        "github.com/renanrodm".center(60),
        end="*",
    )
    print("\n*", "*".rjust(61))
    print("*" * 63)