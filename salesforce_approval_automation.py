#!/usr/bin/env python3
"""
Script minimalista para automação de aprovações do Salesforce
Monitora solicitações de aprovação e processa automaticamente com base em dados CSV
"""

import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class SalesforceApprovalAutomation:
    """Classe para automação de aprovações no Salesforce"""
    
    def __init__(self, csv_file='aprovacoes_permitidas.csv', headless=True):
        """
        Inicializa o automator
        
        Args:
            csv_file: Caminho para o arquivo CSV com dados de aprovação
            headless: Se True, executa o navegador em modo headless
        """
        self.csv_file = csv_file
        self.aprovacoes_permitidas = self._carregar_aprovacoes_csv()
        self.driver = self._inicializar_driver(headless)
        
    def _inicializar_driver(self, headless):
        """Inicializa o Chrome WebDriver em modo headless"""
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
        
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--start-maximized')
        
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    
    def _carregar_aprovacoes_csv(self):
        """
        Carrega dados do CSV com aprovações permitidas
        
        Returns:
            dict: Dicionário com chave (vendedor, comercio) e valor True
        """
        aprovacoes = {}
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    vendedor = row.get('vendedor', '').strip().lower()
                    comercio = row.get('comercio', '').strip().lower()
                    status = row.get('aprovar', 'nao').strip().lower()
                    
                    if status in ['sim', 'yes', 's', 'y', 'true', '1']:
                        chave = (vendedor, comercio)
                        aprovacoes[chave] = True
                        
            print(f"✓ Carregadas {len(aprovacoes)} aprovações do arquivo {self.csv_file}")
            return aprovacoes
            
        except FileNotFoundError:
            print(f"⚠ Arquivo {self.csv_file} não encontrado. Usando lista vazia.")
            return {}
        except Exception as e:
            print(f"⚠ Erro ao carregar CSV: {e}")
            return {}
    
    def navegar_para_url(self, url):
        """
        Navega para a URL especificada
        
        Args:
            url: URL do Salesforce a ser acessada
        """
        print(f"Navegando para {url}...")
        self.driver.get(url)
        time.sleep(2)
    
    def _verificar_aprovacao_permitida(self, vendedor, comercio):
        """
        Verifica se a combinação vendedor/comercio está na lista de aprovações
        
        Args:
            vendedor: Nome do vendedor
            comercio: Nome do comércio/varejo
            
        Returns:
            bool: True se aprovação é permitida
        """
        vendedor_lower = vendedor.strip().lower()
        comercio_lower = comercio.strip().lower()
        chave = (vendedor_lower, comercio_lower)
        return chave in self.aprovacoes_permitidas
    
    def buscar_solicitacoes_pendentes(self):
        """
        Busca todas as solicitações de aprovação pendentes na página
        
        Returns:
            list: Lista de dicionários com informações das solicitações
        """
        solicitacoes = []
        
        try:
            # Aguarda a página carregar
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Seletores comuns para solicitações de aprovação no Salesforce
            # Pode precisar ajustar conforme a interface específica
            seletores_possiveis = [
                "//div[contains(@class, 'approval')]//tr[contains(@class, 'dataRow')]",
                "//table[contains(@class, 'list')]//tr[contains(@class, 'dataRow')]",
                "//div[contains(@class, 'forceListViewManagerGrid')]//tr",
                "//records-lwc-list//tbody//tr",
                "//table//tbody//tr[contains(@class, 'slds-hint-parent')]"
            ]
            
            elementos_encontrados = []
            for seletor in seletores_possiveis:
                try:
                    elementos = self.driver.find_elements(By.XPATH, seletor)
                    if elementos:
                        elementos_encontrados = elementos
                        print(f"✓ Encontrados {len(elementos)} elementos com seletor: {seletor}")
                        break
                except:
                    continue
            
            if not elementos_encontrados:
                print("⚠ Nenhum elemento de solicitação encontrado na página")
                return solicitacoes
            
            # Processa cada linha encontrada
            for idx, elemento in enumerate(elementos_encontrados, 1):
                try:
                    texto_completo = elemento.text.strip()
                    
                    if not texto_completo or len(texto_completo) < 3:
                        continue
                    
                    # Tenta extrair informações da solicitação
                    # Procura por nomes típicos de campos
                    vendedor = self._extrair_campo(elemento, ['vendedor', 'seller', 'salesperson', 'submitted by'])
                    comercio = self._extrair_campo(elemento, ['comercio', 'varejo', 'store', 'account', 'customer'])
                    
                    if vendedor and comercio:
                        solicitacao = {
                            'indice': idx,
                            'vendedor': vendedor,
                            'comercio': comercio,
                            'elemento': elemento,
                            'texto': texto_completo
                        }
                        solicitacoes.append(solicitacao)
                        print(f"  Solicitação {idx}: {vendedor} - {comercio}")
                        
                except Exception as e:
                    print(f"  Erro ao processar elemento {idx}: {e}")
                    continue
            
            print(f"\n✓ Total de {len(solicitacoes)} solicitações identificadas")
            return solicitacoes
            
        except TimeoutException:
            print("⚠ Timeout ao buscar solicitações")
            return []
        except Exception as e:
            print(f"✗ Erro ao buscar solicitações: {e}")
            return []
    
    def _extrair_campo(self, elemento, possiveis_nomes):
        """
        Tenta extrair um campo específico do elemento
        
        Args:
            elemento: Elemento Selenium
            possiveis_nomes: Lista de possíveis nomes do campo
            
        Returns:
            str: Valor do campo ou None
        """
        try:
            # Tenta encontrar por label/texto
            for nome in possiveis_nomes:
                # Busca por células com o nome do campo
                xpath_queries = [
                    f".//td[contains(@class, '{nome}')]",
                    f".//span[contains(@class, '{nome}')]",
                    f".//div[contains(@class, '{nome}')]",
                    f".//td[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{nome.lower()}')]"
                ]
                
                for query in xpath_queries:
                    try:
                        campo = elemento.find_element(By.XPATH, query)
                        valor = campo.text.strip()
                        if valor:
                            return valor
                    except:
                        continue
            
            # Se não encontrou por nome específico, tenta extrair das células
            try:
                celulas = elemento.find_elements(By.TAG_NAME, "td")
                if len(celulas) >= 2:
                    # Geralmente vendedor está nas primeiras colunas e comercio também
                    # Retorna baseado na ordem dos possiveis_nomes
                    if 'vendedor' in possiveis_nomes[0].lower() and len(celulas) > 0:
                        return celulas[0].text.strip()
                    if 'comercio' in possiveis_nomes[0].lower() and len(celulas) > 1:
                        return celulas[1].text.strip()
            except:
                pass
                
        except Exception:
            pass
        
        return None
    
    def aprovar_solicitacao(self, solicitacao):
        """
        Aprova uma solicitação específica
        
        Args:
            solicitacao: Dicionário com informações da solicitação
            
        Returns:
            bool: True se aprovação foi bem-sucedida
        """
        try:
            vendedor = solicitacao['vendedor']
            comercio = solicitacao['comercio']
            elemento = solicitacao['elemento']
            
            print(f"\n→ Processando aprovação: {vendedor} - {comercio}")
            
            # Verifica se a aprovação é permitida
            if not self._verificar_aprovacao_permitida(vendedor, comercio):
                print(f"  ✗ Aprovação não permitida (não está no CSV)")
                return False
            
            print(f"  ✓ Aprovação permitida pelo CSV")
            
            # Procura pelo botão de aprovação
            botoes_possiveis = [
                ".//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'approve')]",
                ".//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'aprovar')]",
                ".//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'approve')]",
                ".//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'aprovar')]",
                ".//input[@type='button' and contains(@value, 'Approve')]",
                ".//input[@type='button' and contains(@value, 'Aprovar')]"
            ]
            
            botao_encontrado = None
            for xpath_botao in botoes_possiveis:
                try:
                    botao = elemento.find_element(By.XPATH, xpath_botao)
                    if botao.is_displayed() and botao.is_enabled():
                        botao_encontrado = botao
                        break
                except:
                    continue
            
            if not botao_encontrado:
                # Tenta buscar em toda a linha ou área próxima
                try:
                    # Clica na linha primeiro para selecioná-la
                    elemento.click()
                    time.sleep(1)
                    
                    # Busca botão de aprovação na página
                    for xpath_botao in botoes_possiveis:
                        try:
                            xpath_global = xpath_botao.replace(".", "//")
                            botao = self.driver.find_element(By.XPATH, xpath_global)
                            if botao.is_displayed() and botao.is_enabled():
                                botao_encontrado = botao
                                break
                        except:
                            continue
                except:
                    pass
            
            if botao_encontrado:
                try:
                    # Scroll até o botão
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", botao_encontrado)
                    time.sleep(0.5)
                    
                    # Clica no botão
                    botao_encontrado.click()
                    print(f"  ✓ Clique no botão de aprovação executado")
                    
                    # Aguarda processamento
                    time.sleep(2)
                    
                    # Verifica se há modal de confirmação
                    try:
                        botao_confirmar = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((By.XPATH, 
                                "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'confirm')] | " +
                                "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'confirmar')] | " +
                                "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'ok')] | " +
                                "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'submit')]"
                            ))
                        )
                        botao_confirmar.click()
                        print(f"  ✓ Confirmação executada")
                        time.sleep(2)
                    except TimeoutException:
                        print(f"  → Nenhum modal de confirmação detectado")
                    
                    print(f"  ✓ Aprovação concluída com sucesso!")
                    return True
                    
                except Exception as e:
                    print(f"  ✗ Erro ao clicar no botão: {e}")
                    return False
            else:
                print(f"  ✗ Botão de aprovação não encontrado")
                return False
                
        except Exception as e:
            print(f"  ✗ Erro ao processar aprovação: {e}")
            return False
    
    def monitorar_e_processar(self, url, intervalo=30, max_iteracoes=None):
        """
        Monitora continuamente a página e processa aprovações
        
        Args:
            url: URL do Salesforce a ser monitorada
            intervalo: Tempo em segundos entre verificações (padrão: 30s)
            max_iteracoes: Número máximo de iterações (None = infinito)
        """
        self.navegar_para_url(url)
        
        iteracao = 0
        print(f"\n{'='*60}")
        print(f"MONITORAMENTO INICIADO")
        print(f"URL: {url}")
        print(f"Intervalo: {intervalo}s")
        print(f"{'='*60}\n")
        
        try:
            while True:
                iteracao += 1
                print(f"\n[Iteração {iteracao}] {time.strftime('%H:%M:%S')}")
                print("-" * 60)
                
                # Atualiza a página
                self.driver.refresh()
                time.sleep(3)
                
                # Busca solicitações pendentes
                solicitacoes = self.buscar_solicitacoes_pendentes()
                
                if solicitacoes:
                    aprovadas = 0
                    for solicitacao in solicitacoes:
                        if self.aprovar_solicitacao(solicitacao):
                            aprovadas += 1
                            time.sleep(2)  # Pausa entre aprovações
                    
                    print(f"\n{'='*60}")
                    print(f"Resultado: {aprovadas} de {len(solicitacoes)} aprovadas")
                    print(f"{'='*60}")
                else:
                    print("→ Nenhuma solicitação pendente encontrada")
                
                # Verifica se deve parar
                if max_iteracoes and iteracao >= max_iteracoes:
                    print(f"\n✓ Número máximo de iterações ({max_iteracoes}) atingido")
                    break
                
                # Aguarda próxima verificação
                print(f"\n⏳ Aguardando {intervalo}s até próxima verificação...")
                time.sleep(intervalo)
                
        except KeyboardInterrupt:
            print(f"\n\n⚠ Monitoramento interrompido pelo usuário")
        except Exception as e:
            print(f"\n\n✗ Erro no monitoramento: {e}")
        finally:
            print(f"\nEncerrando...")
    
    def fechar(self):
        """Fecha o navegador"""
        if self.driver:
            self.driver.quit()
            print("✓ Navegador fechado")


def main():
    """Função principal"""
    import sys
    
    # Configuração
    CSV_FILE = 'aprovacoes_permitidas.csv'
    HEADLESS = True  # Modo headless para Codespaces
    INTERVALO_SEGUNDOS = 30  # Intervalo entre verificações
    
    # URL do Salesforce (ajustar conforme necessário)
    # Exemplo: https://your-instance.salesforce.com/approval-page
    SALESFORCE_URL = "https://your-salesforce-instance.lightning.force.com/lightning/o/ProcessInstanceWorkitem/list"
    
    # Se URL foi passada como argumento
    if len(sys.argv) > 1:
        SALESFORCE_URL = sys.argv[1]
    
    print("="*60)
    print("SALESFORCE APPROVAL AUTOMATION")
    print("="*60)
    print(f"Arquivo CSV: {CSV_FILE}")
    print(f"Modo Headless: {HEADLESS}")
    print(f"Intervalo: {INTERVALO_SEGUNDOS}s")
    print("="*60)
    
    automator = None
    try:
        # Inicializa o automator
        automator = SalesforceApprovalAutomation(
            csv_file=CSV_FILE,
            headless=HEADLESS
        )
        
        # Inicia monitoramento
        # Para teste, limitar a 3 iterações. Para produção, remover max_iteracoes
        automator.monitorar_e_processar(
            url=SALESFORCE_URL,
            intervalo=INTERVALO_SEGUNDOS,
            max_iteracoes=None  # None = execução contínua
        )
        
    except Exception as e:
        print(f"\n✗ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if automator:
            automator.fechar()


if __name__ == "__main__":
    main()
