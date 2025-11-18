import time
from jogo_da_adivinhacao_renan_martins.cartelas import geraCartelas, exibeCartela
from jogo_da_adivinhacao_renan_martins.validacao import (
    validaRespostaUsuario,
    verificaContinuacao,
)
from jogo_da_adivinhacao_renan_martins.exibicao import (
    exibeMensagemFinal,
    exibeMensagemInicial,
    exibeValorEscolhido,
)


def main():

    while True:
        exibeMensagemInicial()

        cartelas = geraCartelas()

        valorEscolhido = 0

        for pos, cartela in enumerate(cartelas):

            exibeCartela(cartela, pos)

            if validaRespostaUsuario():
                valorEscolhido += cartela[0]

        exibeValorEscolhido(valorEscolhido)

        if not verificaContinuacao():
            break

    time.sleep(3)
    print()
    exibeMensagemFinal()


if __name__ == "__main__":
    main()
