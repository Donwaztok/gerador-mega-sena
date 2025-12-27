"""
Gerador de Números para Mega Sena

IMPORTANTE: Este gerador usa análise estatística de sorteios anteriores,
mas a Mega Sena é um jogo de sorte puro. Cada combinação tem exatamente
a mesma probabilidade de ser sorteada (1 em 50.063.860).

Análise de frequência histórica NÃO aumenta suas chances de ganhar.
Este programa apenas oferece estratégias baseadas em padrões observados.
"""

import argparse
import sys
from core.gerador import Gerador

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Gerador de Números para Mega Sena baseado em análise estatística"
    )
    parser.add_argument(
        "--force-update",
        action="store_true",
        help="Força a atualização dos dados dos sorteios (baixa novamente da API)"
    )
    parser.add_argument(
        "--quantidade-jogos",
        type=int,
        default=30,
        help="Quantidade de jogos a serem gerados (padrão: 10)"
    )

    args = parser.parse_args()

    print("="*60)
    print("GERADOR DE NÚMEROS PARA MEGA SENA")
    print("="*60)
    print("\nIniciando análise dos sorteios históricos...")
    if args.force_update:
        print("⚠️  Modo: Forçando atualização dos dados (pode levar alguns minutos)\n")
    else:
        print("(Isso pode levar alguns minutos na primeira execução)\n")

    try:
        gerador = Gerador(
            force_get_data=args.force_update,
            quantidade_jogos=args.quantidade_jogos
        )

        print("\n" + "="*60)
        print("Análise concluída!")
        print("="*60)
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Erro durante a execução: {e}")
        sys.exit(1)
