# Salesforce Approval Automation Bot

Mini projeto de soluções para Salesforce - foco em automação de aprovações de solicitações externas de vendedores.

## 📋 Descrição

Script minimalista em Python usando Selenium para automatizar o monitoramento e aprovação de solicitações no Salesforce. Otimizado para rodar no GitHub Codespaces.

### Funcionalidades

✅ Monitora página do Salesforce para identificar novas solicitações de aprovação  
✅ Integra dados com arquivo CSV para regras de aprovação  
✅ Automatiza cliques de aprovação no painel do gerente  
✅ Modo headless para execução em terminal  
✅ Um único arquivo .py limpo e focado  
✅ Otimizado para GitHub Codespaces  

## 🚀 Instalação

### Pré-requisitos

- Python 3.8+
- Google Chrome ou Chromium
- ChromeDriver (instalado automaticamente pelo Selenium)

### Setup no GitHub Codespaces

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Instalar Chrome (se necessário no Codespaces)
sudo apt-get update
sudo apt-get install -y chromium-browser chromium-chromedriver

# 3. Verificar instalação
python salesforce_approval_bot.py --help
```

### Setup Local

```bash
# 1. Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Executar
python salesforce_approval_bot.py --url "sua-url-salesforce"
```

## 💻 Uso

### Comando Básico

```bash
python salesforce_approval_bot.py --url "https://your-salesforce.com/approvals"
```

### Opções Disponíveis

| Opção | Descrição | Padrão |
|-------|-----------|--------|
| `--url` | URL da página de aprovações do Salesforce (obrigatório) | - |
| `--csv` | Arquivo CSV com regras de aprovação | `approvals_data.csv` |
| `--interval` | Intervalo entre verificações (segundos) | `10` |
| `--max-iterations` | Número máximo de verificações | `infinito` |
| `--no-headless` | Executar navegador em modo visível | `headless` |

### Exemplos

**Monitoramento contínuo (padrão):**
```bash
python salesforce_approval_bot.py --url "https://your-salesforce.com/approvals"
```

**Verificar a cada 30 segundos:**
```bash
python salesforce_approval_bot.py --url "https://..." --interval 30
```

**Executar 5 iterações (teste):**
```bash
python salesforce_approval_bot.py --url "https://..." --max-iterations 5
```

**Usar arquivo CSV customizado:**
```bash
python salesforce_approval_bot.py --url "https://..." --csv minhas_regras.csv
```

**Modo visível (debug):**
```bash
python salesforce_approval_bot.py --url "https://..." --no-headless
```

## 📊 Formato do CSV

O arquivo `approvals_data.csv` define quais solicitações devem ser aprovadas automaticamente:

```csv
request_id,auto_approve,notes
REQ-001,true,Vendedor aprovado - João Silva
REQ-002,true,Vendedor aprovado - Maria Santos
REQ-003,false,Necessita revisão manual
AP-12345,true,Aprovação automática configurada
```

**Colunas:**
- `request_id`: ID da solicitação no Salesforce
- `auto_approve`: `true` para aprovar automaticamente, `false` para ignorar
- `notes`: Notas/comentários (opcional)

## 🔧 Configuração

### Adaptando para Sua Página Salesforce

O script usa seletores comuns, mas você pode precisar ajustá-los para sua instância específica do Salesforce. Edite as seguintes seções em `salesforce_approval_bot.py`:

**1. Seletores de Solicitações (linha ~116):**
```python
selectors = [
    "//div[contains(@class, 'approval-item')]",
    "//tr[contains(@class, 'approval-request')]",
    # Adicione seus seletores específicos aqui
]
```

**2. Seletores de Botões de Aprovação (linha ~171):**
```python
approve_buttons = [
    ".//button[contains(., 'Approve') or contains(., 'Aprovar')]",
    # Adicione seus seletores específicos aqui
]
```

### Como Encontrar Seletores

1. Abra a página do Salesforce no navegador
2. Pressione F12 para abrir DevTools
3. Use o seletor de elementos (ícone de seta)
4. Clique no elemento de aprovação
5. No HTML, veja as classes e atributos do elemento

## 📝 Estrutura do Projeto

```
salesforcepy01/
├── salesforce_approval_bot.py  # Script principal
├── approvals_data.csv          # Regras de aprovação
├── requirements.txt            # Dependências Python
├── .gitignore                  # Arquivos ignorados pelo Git
└── README.md                   # Documentação
```

## 🛡️ Segurança

⚠️ **Importante:**
- Nunca commite credenciais no código
- Use variáveis de ambiente para dados sensíveis
- O script assume que você já está autenticado no Salesforce
- Mantenha o arquivo CSV com regras de aprovação seguro

## 🐛 Troubleshooting

### Chrome/ChromeDriver não encontrado
```bash
# Instalar Chrome no Ubuntu/Codespaces
sudo apt-get update
sudo apt-get install -y chromium-browser chromium-chromedriver
```

### Elementos não encontrados
- Verifique se os seletores CSS/XPath estão corretos para sua página
- Use `--no-headless` para ver o navegador e debugar
- Aumente o tempo de espera implícito se a página carrega lentamente

### CSV não carregado
- Verifique se o arquivo existe no diretório correto
- Confirme que o encoding é UTF-8
- Verifique o formato das colunas

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se livre para:
- Reportar bugs
- Sugerir novas funcionalidades
- Enviar pull requests

## 📄 Licença

Este projeto é open source e está disponível sob a licença MIT.

## 👤 Autor

Desenvolvido para automação de aprovações no Salesforce.
