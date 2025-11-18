"""Módulo responsável pela validação de entrada de dados"""


def validaRespostaUsuario():
    opcoes_validas = ("s", "n")
    while True:
        try:
            resposta = input("\nO valor escolhido está nessa cartela (s/n)?: ")

            if not resposta:
                raise ValueError("Resposta não pode ser vazia")

            if resposta not in opcoes_validas:
                raise ValueError("Digite apenas 's' ou 'n'")

            if resposta == "s":
                return True
            elif resposta == "n":
                return False

        except ValueError as e:
            print(f"Erro: {e}")
        except Exception as e:
            print(f"Erro inesperado: {e}")


def verificaContinuacao():

    opcoesValidasParaContinuar = "s"
    opcoesValidasParaInterromper = "n"

    while True:
        respostaUsuario = input("\n\nDeseja jogar novamente?? (s/n): ")

        if not respostaUsuario:
            raise ValueError("Resposta não pode ser vazia")

        if respostaUsuario in opcoesValidasParaContinuar:
            return True
        elif respostaUsuario in opcoesValidasParaInterromper:
            return False
        else:
            raise ValueError("Digite apenas 's' ou 'n'")
