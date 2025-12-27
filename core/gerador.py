import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Counter

import matplotlib.pyplot as plt
import numpy as np
import requests
import urllib3
from scipy import stats

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Gerador():
    # Função para fazer uma solicitação GET ao endpoint e salvar a resposta
    def get_json(self, id, max_retries=20):
        url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/megasena/{id}"
        retries = 0
        while retries < max_retries:
            response = requests.get(url, verify=False)
            # Verificar se a requisição foi bem-sucedida
            if response.status_code == 200:
                data = response.json()
                print(f"Sucesso na requisição para o ID {id}.")
                return id, data
            else:
                print(f"Erro na requisição do ID {id}: {response.status_code}. Tentando novamente...")
                retries += 1
                time.sleep(1)  # Pausa antes de tentar novamente
        print(f"Falha após {max_retries} tentativas.")
        return None

    def check_repetitions(self, conjunto, conjuntos_frequentes, max_repetitions=2):
        """
        Verifica se um conjunto tem no máximo max_repetitions números em comum
        com qualquer conjunto já existente na lista.
        """
        for conjunto_frequente in conjuntos_frequentes:
            # Conta quantos números são comuns entre os dois conjuntos
            numeros_comuns = len(set(conjunto) & set(conjunto_frequente))
            if numeros_comuns > max_repetitions:
                return False
        return True

    def get_all_data(self):
        # Crie uma lista para armazenar todos os threads
        self.threads = []

        # Crie um dicionário para armazenar as respostas
        self.responses = {}

        # Obter o último id
        url = "https://servicebus2.caixa.gov.br/portaldeloterias/api/megasena/"
        data = requests.get(url, verify=False).json()
        self.last_id = data['numero']
        self.responses[self.last_id] = data

        # Crie um pool de threads e faça cada thread executar a função get_json
        with ThreadPoolExecutor() as executor:
            future_to_id = {executor.submit(self.get_json, id): id for id in range(1, self.last_id)}
            for future in as_completed(future_to_id):
                data = future.result()
                if data is not None:
                    self.responses[data[0]] = data[1]

        # Ordenar as respostas por ID
        self.responses = dict(sorted(self.responses.items()))

        # Salve as respostas em um arquivo JSON
        with open('output.json', 'w') as f:
            json.dump(self.responses, f, indent=4)  # Adicionado indentação aqui

    def gerar_combinacao_otimizada(self, numeros, counter, quantidade=5):
        """
        Gera combinações otimizadas usando estratégia baseada em frequências.
        Prioriza números com maior frequência histórica.
        """
        conjuntos = []
        numeros_ordenados = sorted(numeros, key=lambda x: counter[x], reverse=True)

        # Estratégia simplificada para evitar loops infinitos
        max_tentativas = min(quantidade * 2, 30)  # Limita tentativas

        for i in range(max_tentativas):
            if len(conjuntos) >= quantidade:
                break

            conjunto = []

            # Sempre inclui alguns dos top números mais frequentes
            offset = i % max(1, len(numeros_ordenados) - 5)
            top_count = min(3, len(numeros_ordenados))

            for j in range(top_count):
                idx = (offset + j) % len(numeros_ordenados)
                num = numeros_ordenados[idx]
                if num not in conjunto:
                    conjunto.append(num)

            # Preenche o resto de forma simples e direta
            tentativas_preenchimento = 0
            while len(conjunto) < 6 and tentativas_preenchimento < len(numeros_ordenados):
                idx = (i * 3 + len(conjunto) + tentativas_preenchimento) % len(numeros_ordenados)
                num = numeros_ordenados[idx]
                if num not in conjunto:
                    conjunto.append(num)
                tentativas_preenchimento += 1

            # Se ainda não tiver 6, completa com os mais frequentes disponíveis
            if len(conjunto) < 6:
                for num in numeros_ordenados:
                    if num not in conjunto and len(conjunto) < 6:
                        conjunto.append(num)
                        if len(conjunto) >= 6:
                            break

            if len(conjunto) < 6:
                continue

            conjunto = sorted(conjunto[:6])

            # Verifica se é válido e diversificado (com restrição mais flexível)
            max_repetitions = 4 if len(conjuntos) > quantidade // 2 else 3
            if len(conjunto) == 6 and self.check_repetitions(conjunto, conjuntos, max_repetitions=max_repetitions):
                conjuntos.append(tuple(conjunto))

        return conjuntos

    def gerar_grafico_frequencias(self, counter, total_sorteios, freq_esperada, numeros_ouro):
        """
        Gera um gráfico de barras mostrando a frequência de cada número.
        """
        # Preparar dados
        numeros = list(range(1, 61))
        frequencias = [counter.get(num, 0) for num in numeros]

        # Identificar números de ouro
        nums_ouro = {num for num, _, _, _ in numeros_ouro}

        # Criar figura com tamanho maior
        plt.figure(figsize=(16, 8))

        # Criar cores: dourado para números de ouro, azul para os demais
        cores = ['#FFD700' if num in nums_ouro else '#4A90E2' for num in numeros]

        # Criar gráfico de barras
        bars = plt.bar(numeros, frequencias, color=cores, alpha=0.8, edgecolor='black', linewidth=0.5)

        # Adicionar linha da média esperada
        plt.axhline(y=freq_esperada, color='red', linestyle='--', linewidth=2,
                   label=f'Média Esperada ({freq_esperada:.1f})', alpha=0.7)

        # Personalizar gráfico
        plt.xlabel('Números (1-60)', fontsize=12, fontweight='bold')
        plt.ylabel('Frequência (Quantas vezes apareceu)', fontsize=12, fontweight='bold')
        plt.title(f'Frequência de Aparição dos Números na Mega Sena\n'
                 f'({total_sorteios} sorteios analisados)',
                 fontsize=14, fontweight='bold', pad=20)
        plt.grid(axis='y', alpha=0.3, linestyle=':')

        # Ajustar eixos
        plt.xlim(0, 61)
        plt.xticks(range(1, 61, 2), rotation=45, ha='right')  # Mostrar números ímpares para não ficar muito cheio

        # Adicionar anotações para os top números
        top_5 = counter.most_common(5)
        for num, freq in top_5:
            plt.annotate(f'{freq}',
                        xy=(num, freq),
                        xytext=(num, freq + max(frequencias) * 0.02),
                        ha='center', va='bottom',
                        fontsize=8, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))

        # Adicionar legenda de cores
        from matplotlib.patches import Patch
        from matplotlib.lines import Line2D
        legend_elements = [
            Patch(facecolor='#FFD700', edgecolor='black', label='Números de Ouro'),
            Patch(facecolor='#4A90E2', edgecolor='black', label='Outros Números'),
            Line2D([0], [0], color='red', linestyle='--', linewidth=2, label=f'Média Esperada ({freq_esperada:.1f})')
        ]
        plt.legend(handles=legend_elements, loc='upper right', fontsize=10)

        # Ajustar layout
        plt.tight_layout()

        # Salvar gráfico
        nome_arquivo = 'grafico_frequencias_mega_sena.png'
        plt.savefig(nome_arquivo, dpi=300, bbox_inches='tight')
        print(f"\n📊 Gráfico salvo como: {nome_arquivo}")

        # Mostrar gráfico (opcional - pode comentar se não quiser abrir automaticamente)
        # plt.show()
        plt.close()

    def teste_uniformidade_qui_quadrado(self, counter, total_sorteios):
        """
        Realiza teste qui-quadrado para verificar se a distribuição é uniforme.
        Retorna estatística do teste, p-value e conclusão.
        """
        # Frequência esperada por número
        freq_esperada = (6 * total_sorteios) / 60

        # Frequências observadas para todos os números (1-60)
        frequencias_observadas = [counter.get(num, 0) for num in range(1, 61)]
        frequencias_esperadas = [freq_esperada] * 60

        # Teste qui-quadrado
        chi2_stat, p_value = stats.chisquare(frequencias_observadas, frequencias_esperadas)

        # Graus de liberdade (60 números - 1)
        df = 59

        # Interpretação
        alpha = 0.05  # Nível de significância de 5%
        if p_value < alpha:
            conclusao = "REJEITA uniformidade"
            interpretacao = "As diferenças são estatisticamente significativas (p < 0.05)."
            interpretacao += "\n   Isso sugere que pode haver viés no processo físico de sorteio."
        else:
            conclusao = "NÃO REJEITA uniformidade"
            interpretacao = "As diferenças podem ser explicadas por variação aleatória (p >= 0.05)."

        return chi2_stat, p_value, df, conclusao, interpretacao, freq_esperada

    def analisar_numeros_ouro(self, counter, total_sorteios):
        """
        Identifica os 'números de ouro' - números que aparecem com frequência
        significativamente acima da média esperada.
        """
        # Frequência esperada por número (6 números por sorteio)
        freq_esperada = (6 * total_sorteios) / 60

        numeros_ouro = []
        numeros_comuns = []
        numeros_ruins = []

        for num in range(1, 61):  # Mega Sena vai de 1 a 60
            freq_real = counter.get(num, 0)
            diferenca = freq_real - freq_esperada
            percentual = (freq_real / total_sorteios * 100) if total_sorteios > 0 else 0

            if diferenca > freq_esperada * 0.2:  # 20% acima da média
                numeros_ouro.append((num, freq_real, percentual, diferenca))
            elif diferenca < -freq_esperada * 0.2:  # 20% abaixo da média
                numeros_ruins.append((num, freq_real, percentual, diferenca))
            else:
                numeros_comuns.append((num, freq_real, percentual, diferenca))

        # Ordenar por frequência
        numeros_ouro.sort(key=lambda x: x[1], reverse=True)
        numeros_ruins.sort(key=lambda x: x[1])

        return numeros_ouro, numeros_comuns, numeros_ruins, freq_esperada

    def run_generator(self, quantidade_jogos=10):
        """
        IMPORTANTE SOBRE PROBABILIDADE:

        A Mega Sena é um jogo de sorte puro onde cada sorteio é INDEPENDENTE.
        Isso significa que o resultado de um sorteio não influencia o próximo.

        Por exemplo: se o número 10 apareceu 200 vezes nos últimos 1000 sorteios,
        isso NÃO significa que ele tem mais chance de aparecer no próximo sorteio.
        Cada número tem exatamente 1/60 de chance de ser sorteado em cada posição.

        Os "números de ouro" são apenas uma curiosidade estatística do passado,
        não uma garantia do futuro. É como jogar uma moeda: mesmo que tenha dado
        cara 10 vezes seguidas, a chance de dar cara na próxima ainda é 50%.

        Cada combinação de 6 números tem exatamente a mesma probabilidade:
        1 em 50.063.860 (independente de quais números você escolher).
        """
        # Carregar o arquivo JSON
        with open('output.json', 'r') as f:
            data = json.load(f)

        # Contar as ocorrências dos números
        counter = Counter()
        for id, item in data.items():
            if 'listaDezenas' in item:
                # Converter strings para inteiros
                dezenas = [int(d) for d in item['listaDezenas']]
                counter.update(dezenas)
            else:
                print(f'O item com ID {id} não possui "listaDezenas".')

        if not counter:
            print("Erro: Nenhum dado encontrado para análise.")
            return

        total_sorteios = len(data)

        # Análise dos números de ouro
        numeros_ouro, numeros_comuns, numeros_ruins, freq_esperada = self.analisar_numeros_ouro(
            counter, total_sorteios
        )

        # ANÁLISE ESTATÍSTICA RIGOROSA (resumida)
        chi2_stat, p_value, df, conclusao, interpretacao, _ = self.teste_uniformidade_qui_quadrado(
            counter, total_sorteios
        )

        print("\n" + "="*70)
        print("🔬 ANÁLISE ESTATÍSTICA")
        print("="*70)
        print(f"Teste Qui-quadrado: {chi2_stat:.2f} | P-value: {p_value:.6f} | {conclusao}")

        if p_value < 0.05:
            print("⚠️  Viés detectado! Os números de ouro podem ter vantagem real.")
        else:
            print("✅ Sem viés detectado. Diferenças podem ser apenas aleatórias.")

        # Vetor de gerados
        gerados = []

        # NÚMEROS DE OURO (resumido)
        print("\n" + "="*70)
        print("🌟 NÚMEROS DE OURO")
        print("="*70)
        print(f"Total de sorteios analisados: {total_sorteios}")

        if numeros_ouro:
            print(f"\nTop 10 números mais frequentes:")
            for num, freq, percent, diff in numeros_ouro[:10]:
                print(f"  {num:2d}: {freq:3d} vezes ({percent:5.2f}%) | +{diff:+.1f} acima da média")
        else:
            # Se não há números de ouro, mostra os top frequentes
            top_freq = counter.most_common(10)
            print(f"\nTop 10 números mais frequentes:")
            for num, freq in top_freq:
                percent = (freq / total_sorteios * 100) if total_sorteios > 0 else 0
                diff = freq - freq_esperada
                print(f"  {num:2d}: {freq:3d} vezes ({percent:5.2f}%) | {diff:+.1f} vs esperado")

        # GERA COMBINAÇÕES (sem mostrar logs intermediários)
        gerados = []

        if numeros_ouro:
            # Pegar os top números de ouro (ou top 20 se houver menos)
            nums_ouro = [num for num, _, _, _ in numeros_ouro[:20]]
            if len(nums_ouro) < 20:
                # Completar com os mais frequentes em geral
                mais_freq_geral = [num for num, _ in counter.most_common(20)]
                for num in mais_freq_geral:
                    if num not in nums_ouro and len(nums_ouro) < 20:
                        nums_ouro.append(num)

            # Gera combinações com números de ouro
            # Gera muito mais jogos para garantir que após os filtros tenhamos quantidade_jogos
            # Multiplica por 4 para ter margem após filtros de qualidade (90%) e repetição
            conjuntos_ouro = self.gerar_combinacao_otimizada(
                nums_ouro, counter, quantidade=quantidade_jogos * 4
            )
            gerados.extend([sorted(c) for c in conjuntos_ouro])

        # Gera combinações adicionais usando apenas números de alta frequência
        # Usa top 25 números para garantir alta qualidade
        mais_frequentes_nums = [num for num, _ in counter.most_common(25)]
        conjuntos_mais_freq = self.gerar_combinacao_otimizada(
            mais_frequentes_nums, counter, quantidade=quantidade_jogos * 2
        )
        gerados.extend([sorted(c) for c in conjuntos_mais_freq])

        # Combinações usando top números (sem misturar com menos frequentes)
        # Foca apenas em números de alta qualidade
        top_numeros = [num for num, _ in counter.most_common(30)]
        conjuntos_top = self.gerar_combinacao_otimizada(
            top_numeros, counter, quantidade=quantidade_jogos * 2
        )
        gerados.extend([sorted(c) for c in conjuntos_top])

        # Calcular score ideal teórico (soma dos 6 números mais frequentes)
        top_6_numeros = [num for num, _ in counter.most_common(6)]
        score_ideal = sum(counter.get(n, 0) for n in top_6_numeros)
        score_minimo = int(score_ideal * 0.90)  # Sempre 90% do ideal - apenas alta qualidade

        # Filtrar jogos finais com menos repetição e calcular scores
        print("\n" + "="*70)
        print("🎯 JOGOS FINAIS RECOMENDADOS")
        print("="*70)
        print(f"(Score = soma das frequências históricas | Ideal: {score_ideal} | Mínimo: {score_minimo} (90%))\n")

        possivel_jogo = []
        jogos_com_score = []

        for conj in gerados:
            score = sum(counter.get(n, 0) for n in conj)
            # Só aceita jogos com score >= 90% do ideal
            if score >= score_minimo:
                if self.check_repetitions(conj, possivel_jogo, max_repetitions=3):
                    possivel_jogo.append(conj)
                    jogos_com_score.append((conj, score))

        # Se não temos jogos suficientes, gera mais usando apenas números de alta qualidade
        if len(jogos_com_score) < quantidade_jogos:
            # Usa apenas os top 30 números mais frequentes para garantir alta qualidade
            numeros_alta_qualidade = [num for num, _ in counter.most_common(30)]
            tentativas_extra = 0
            max_tentativas_extra = 20

            while len(jogos_com_score) < quantidade_jogos and tentativas_extra < max_tentativas_extra:
                # Gera mais combinações usando apenas números de alta qualidade
                conjuntos_extra = self.gerar_combinacao_otimizada(
                    numeros_alta_qualidade, counter, quantidade=(quantidade_jogos - len(jogos_com_score)) * 3
                )

                for conj in conjuntos_extra:
                    if len(jogos_com_score) >= quantidade_jogos:
                        break
                    score = sum(counter.get(n, 0) for n in conj)
                    # Mantém o padrão de 90% do ideal
                    if score >= score_minimo:
                        if self.check_repetitions(conj, possivel_jogo, max_repetitions=3):
                            possivel_jogo.append(conj)
                            jogos_com_score.append((conj, score))

                tentativas_extra += 1

        # Ordena por score (maior primeiro)
        jogos_com_score.sort(key=lambda x: x[1], reverse=True)

        # Mostra até a quantidade desejada
        jogos_para_mostrar = min(len(jogos_com_score), quantidade_jogos)

        if jogos_com_score:
            for i, (conjunto, score) in enumerate(jogos_com_score[:jogos_para_mostrar], 1):
                percentual_ideal = (score / score_ideal * 100) if score_ideal > 0 else 0
                print(f"Jogo {i:2d}: {sorted(conjunto)} | Score: {score} ({percentual_ideal:.1f}% do ideal)")

            if len(jogos_com_score) < quantidade_jogos:
                print(f"\n⚠️  Apenas {len(jogos_com_score)} jogos com score >= 90% foram gerados")
                print(f"   (requisito: score >= {score_minimo}). Tente reduzir a quantidade solicitada.")
        else:
            print(f"Nenhum jogo gerado com score >= {score_minimo} (90% do ideal) após filtragem.")


        # Gerar gráfico de frequências (silencioso)
        try:
            self.gerar_grafico_frequencias(counter, total_sorteios, freq_esperada, numeros_ouro)
        except Exception:
            pass  # Falha silenciosamente

    def __init__(self, force_get_data=False, quantidade_jogos=10):
        """
        Inicializa o gerador de números da Mega Sena.

        Args:
            force_get_data: Se True, força o download dos dados da API
            quantidade_jogos: Quantidade de jogos a serem gerados (padrão: 10)
        """
        if not os.path.exists('output.json') or force_get_data:
            self.get_all_data()

        self.run_generator(quantidade_jogos=quantidade_jogos)