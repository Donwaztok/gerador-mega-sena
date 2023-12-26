import concurrent
import json
from concurrent.futures import ThreadPoolExecutor

import requests
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Função para fazer uma solicitação GET ao endpoint e salvar a resposta
def get_json(id):
    url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/megasena/{id}"
    response = requests.get(url, verify=False)
    data = response.json()
    return id, data

class Gerador():
    def __init__(self):
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
            future_to_id = {executor.submit(get_json, id): id for id in range(1, self.last_id)}
            for future in concurrent.futures.as_completed(future_to_id):
                id = future_to_id[future]
                try:
                    data = future.result()
                except Exception as exc:
                    print(f'ID {id} gerou uma exceção: {exc}')
                else:
                    self.responses[data[0]] = data[1]
                    print(f"ID: {data[0]} encontrado")

        # Ordenar as respostas por ID
        self.responses = dict(sorted(self.responses.items()))

        # Salve as respostas em um arquivo JSON
        with open('output.json', 'w') as f:
            json.dump(self.responses, f, indent=4)  # Adicionado indentação aqui
