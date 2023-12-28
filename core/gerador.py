import concurrent
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
from itertools import combinations
from typing import Counter

import requests
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

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
                print(f"Erro na requisição: {response.status_code}. Tentando novamente...")
                retries += 1
                time.sleep(1)  # Pausa antes de tentar novamente
        print(f"Falha após {max_retries} tentativas.")
        return None

    def check_repetitions(self, conjunto, conjuntos_frequentes, max_repetitions=2):
        count = 0
        for num in conjunto:
            for conjunto_frequente in conjuntos_frequentes:
                if num in conjunto_frequente:
                    count += 1
                    if count > max_repetitions:
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
            for future in concurrent.futures.as_completed(future_to_id):
                data = future.result()
                if data is not None:
                    self.responses[data[0]] = data[1]

        # Ordenar as respostas por ID
        self.responses = dict(sorted(self.responses.items()))

        # Salve as respostas em um arquivo JSON
        with open('output.json', 'w') as f:
            json.dump(self.responses, f, indent=4)  # Adicionado indentação aqui

    def run_generator(self):
        # Carregar o arquivo JSON
        with open('output.json', 'r') as f:
            data = json.load(f)

        # Contar as ocorrências dos números
        counter = Counter()
        for id, item in data.items():  # Obter o ID do item
            if 'listaDezenas' in item:  # Verificar se 'listaDezenas' existe
                counter.update(item['listaDezenas'])
            else:
                print(f'O item com ID {id} não possui "listaDezenas".')

        # Gerar todos os conjuntos possíveis de 6 números
        conjuntos = list(combinations(counter.keys(), 6))

        # Ordenar os conjuntos pela soma das ocorrências dos números
        conjuntos.sort(key=lambda x: sum(counter[i] for i in x))

        # Os 5 conjuntos de 6 números que mais aparecem
        mais_frequentes = reversed(conjuntos[-5:])

        # Os 5 conjuntos de 6 números que menos aparecem
        menos_frequentes = conjuntos[:5]

        # Vetor de gerados
        gerados = []

        # print('5 conjuntos de 6 números que mais aparecem:')
        # for conjunto in mais_frequentes:
        #     print(sorted(conjunto))
        #     gerados.append(sorted(conjunto))

        # print('\n5 conjuntos de 6 números que menos aparecem:')
        # for conjunto in menos_frequentes:
        #     print(sorted(conjunto))
        #     gerados.append(sorted(conjunto))

        # Os 5 conjuntos de 6 números que mais aparecem
        mais_frequentes = []
        for conj in reversed(conjuntos):
            if self.check_repetitions(conj, mais_frequentes):
                mais_frequentes.append(conj)
                if len(mais_frequentes) == 5:
                    break

        # Os 5 conjuntos de 6 números que menos aparecem
        menos_frequentes = []
        for conj in conjuntos:
            if self.check_repetitions(conj, menos_frequentes):
                menos_frequentes.append(conj)
                if len(menos_frequentes) == 5:
                    break

        print('5 conjuntos de 6 números que mais aparecem que não se repetem:')
        for conjunto in mais_frequentes:
            print(sorted(conjunto))
            gerados.append(sorted(conjunto))

        print('\n5 conjuntos de 6 números que menos aparecem que não se repetem:')
        for conjunto in menos_frequentes:
            print(sorted(conjunto))
            gerados.append(sorted(conjunto))

        # Pegar os 20 números que mais aparecem
        mais_frequentes = counter.most_common(20)
        mais_frequentes = [num for num, _ in mais_frequentes]

        # Pegar os 20 números que menos aparecem
        menos_frequentes = counter.most_common()[:-21:-1]
        menos_frequentes = [num for num, _ in menos_frequentes]

        # Gerar todos os conjuntos possíveis de 6 números
        conjuntos_mais_frequentes = list(combinations(mais_frequentes, 6))
        conjuntos_menos_frequentes = list(combinations(menos_frequentes, 6))

        # Os 5 conjuntos de 6 números que mais aparecem
        mais_frequentes = []
        for conj in conjuntos_mais_frequentes:
            if self.check_repetitions(conj, mais_frequentes):
                mais_frequentes.append(conj)
                if len(mais_frequentes) == 5:
                    break

        # Os 5 conjuntos de 6 números que menos aparecem
        menos_frequentes = []
        for conj in conjuntos_menos_frequentes:
            if self.check_repetitions(conj, menos_frequentes):
                menos_frequentes.append(conj)
                if len(menos_frequentes) == 5:
                    break

        print('\nConjuntos de 6 números entre os 20 que mais aparecem:')
        for conjunto in mais_frequentes:
            print(sorted(conjunto))
            gerados.append(sorted(conjunto))

        print('\nConjuntos de 6 números entre os 20 que menos aparecem:')
        for conjunto in menos_frequentes:
            print(sorted(conjunto))
            gerados.append(sorted(conjunto))

        # Possivel jogo
        possivel_jogo = []
        for conj in gerados:
            if self.check_repetitions(conj, possivel_jogo, 4):
                possivel_jogo.append(conj)

        if len(possivel_jogo) > 0:
            print('\nPossíveis conjuntos de 6 números:')
            for conjunto in possivel_jogo:
                print(sorted(conjunto))

    def __init__(self, force_get_data=False):
        if not os.path.exists('output.json') or force_get_data:
            self.get_all_data()

        self.run_generator()