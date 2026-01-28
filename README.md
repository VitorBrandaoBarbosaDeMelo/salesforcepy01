# salesforcepy01
Mini projeto de soluções para Sales Force - foco automação de aprovações de solicitações externa de vendedores

## 📋 Descrição

Script minimalista em Python usando Selenium para automação de aprovações no Salesforce, otimizado para rodar no GitHub Codespaces em modo headless.

## ✨ Funcionalidades

- ✅ Monitoramento automático de solicitações de aprovação no Salesforce
- ✅ Integração com arquivo CSV para controle de aprovações permitidas
- ✅ Identificação de solicitações por nome do vendedor e comércio/varejo
- ✅ Aprovação automática baseada em regras do CSV
- ✅ Execução em modo headless (sem interface gráfica)
- ✅ Otimizado para GitHub Codespaces e terminal

## 🚀 Instalação

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Instalar ChromeDriver

No GitHub Codespaces ou Ubuntu:

```bash
# Instalar Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb

# Verificar instalação
google-chrome --version
```

## 📝 Configuração

### Arquivo CSV (aprovacoes_permitidas.csv)

Crie ou edite o arquivo `aprovacoes_permitidas.csv` com a lista de aprovações permitidas:

```csv
vendedor,comercio,aprovar
João Silva,Loja Magazine Luiza,sim
Maria Santos,Carrefour Centro,sim
Pedro Costa,Extra Matriz,sim
```

**Colunas:**
- `vendedor`: Nome do vendedor solicitante
- `comercio`: Nome do comércio/varejo
- `aprovar`: "sim" para aprovar automaticamente, "nao" para ignorar

## 🎯 Uso

### Execução básica

```bash
python salesforce_approval_automation.py
```

### Execução com URL personalizada

```bash
python salesforce_approval_automation.py "https://sua-instancia.salesforce.com/lightning/o/ProcessInstanceWorkitem/list"
```

### Configurações no código

Edite as variáveis no início da função `main()`:

```python
CSV_FILE = 'aprovacoes_permitidas.csv'  # Arquivo CSV
HEADLESS = True                          # Modo headless
INTERVALO_SEGUNDOS = 30                  # Intervalo entre verificações
SALESFORCE_URL = "https://..."           # URL do Salesforce
```

## 🔄 Fluxo de Funcionamento

1. **Carrega aprovações permitidas** do arquivo CSV
2. **Navega** para a página de aprovações do Salesforce
3. **Monitora** continuamente a página em busca de novas solicitações
4. **Identifica** solicitações pelo nome do vendedor e comércio
5. **Verifica** se a aprovação está permitida no CSV
6. **Aprova** automaticamente as solicitações permitidas
7. **Repete** o processo no intervalo configurado

## 📊 Exemplo de Saída

```
============================================================
SALESFORCE APPROVAL AUTOMATION
============================================================
Arquivo CSV: aprovacoes_permitidas.csv
Modo Headless: True
Intervalo: 30s
============================================================

✓ Carregadas 7 aprovações do arquivo aprovacoes_permitidas.csv

Navegando para https://...

============================================================
MONITORAMENTO INICIADO
URL: https://...
Intervalo: 30s
============================================================

[Iteração 1] 10:30:45
------------------------------------------------------------
✓ Encontrados 3 elementos com seletor: ...
  Solicitação 1: João Silva - Loja Magazine Luiza
  Solicitação 2: Maria Santos - Carrefour Centro

✓ Total de 2 solicitações identificadas

→ Processando aprovação: João Silva - Loja Magazine Luiza
  ✓ Aprovação permitida pelo CSV
  ✓ Clique no botão de aprovação executado
  ✓ Aprovação concluída com sucesso!

============================================================
Resultado: 2 de 2 aprovadas
============================================================

⏳ Aguardando 30s até próxima verificação...
```

## 🛠️ Personalização

### Ajustar seletores para sua interface Salesforce

O script inclui múltiplos seletores XPath para compatibilidade com diferentes interfaces do Salesforce. Se necessário, ajuste os seletores na função `buscar_solicitacoes_pendentes()`:

```python
seletores_possiveis = [
    "//div[contains(@class, 'approval')]//tr[contains(@class, 'dataRow')]",
    "//table[contains(@class, 'list')]//tr[contains(@class, 'dataRow')]",
    # Adicione seus seletores personalizados aqui
]
```

## ⚙️ Requisitos

- Python 3.8+
- Google Chrome
- ChromeDriver (compatível com a versão do Chrome)
- Selenium 4.16.0+

## 🔒 Observações de Segurança

- ⚠️ **Não inclua credenciais** no código ou repositório
- ⚠️ Certifique-se de que a **sessão do Salesforce já está autenticada** antes de executar
- ⚠️ Use **variáveis de ambiente** para informações sensíveis
- ⚠️ Teste em ambiente de **desenvolvimento** antes de produção

## 🐛 Troubleshooting

### ChromeDriver não encontrado
```bash
# Instalar via apt (Ubuntu/Debian)
sudo apt install chromium-chromedriver

# Ou baixar manualmente de https://chromedriver.chromium.org/
```

### Elementos não encontrados
- Verifique se está na página correta do Salesforce
- Ajuste os seletores XPath conforme sua interface
- Use o modo não-headless temporariamente para debug: `HEADLESS = False`

### Timeout ou lentidão
- Aumente os valores de `time.sleep()` no código
- Verifique conexão de rede
- Aumente o `INTERVALO_SEGUNDOS`

## 📄 Licença

Este é um projeto educacional para automação de processos no Salesforce.

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.
