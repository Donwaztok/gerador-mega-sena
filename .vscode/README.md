# Configuração de Debug do VS Code

## Pré-requisitos

1. **Criar o ambiente virtual (venv)**:
   ```bash
   python -m venv .venv
   ```

2. **Ativar o ambiente virtual**:
   ```bash
   source .venv/bin/activate  # Linux/Mac
   # ou
   .venv\Scripts\activate     # Windows
   ```

3. **Instalar as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

## Configurações de Debug Disponíveis

### 1. Python: Debug Gerador Mega Sena
- Executa o `main.py` normalmente
- Usa dados existentes (não força atualização)
- Ideal para debug rápido

### 2. Python: Debug Gerador Mega Sena (Forçar Atualização)
- Executa o `main.py` com `--force-update`
- Força o download de todos os dados da API
- Útil para testar a atualização de dados

### 3. Python: Debug Current File
- Debug do arquivo atualmente aberto no editor
- Útil para testar módulos individuais

### 4. Python: Debug Module (core.gerador)
- Debug do módulo `core.gerador` diretamente
- Útil para testar a classe Gerador isoladamente

## Como Usar

1. Abra o arquivo que deseja debugar
2. Coloque breakpoints clicando na margem esquerda (bolinha vermelha)
3. Pressione `F5` ou vá em **Run > Start Debugging**
4. Selecione a configuração desejada no menu dropdown
5. O debug iniciará e parará nos breakpoints

## Dicas

- Use `F10` para Step Over (próxima linha)
- Use `F11` para Step Into (entrar em funções)
- Use `Shift+F11` para Step Out (sair da função)
- Use `F5` para Continue (continuar até o próximo breakpoint)
- Use `Ctrl+Shift+F5` para Reiniciar o debug
- Use `Shift+F5` para Parar o debug

## Variáveis e Watch

- **Variáveis**: Painel lateral mostra todas as variáveis do escopo atual
- **Watch**: Adicione expressões para monitorar valores específicos
- **Call Stack**: Veja a pilha de chamadas de funções
- **Breakpoints**: Gerencie todos os breakpoints em um painel dedicado


