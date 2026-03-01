#!/bin/env python3
"""
Módulo de utilities compartilhado pelo Telegram Scraper
Contém funções de configuração, cores, banner e conexão.
"""

import os
import sys
import configparser
from typing import Optional, Tuple
from pathlib import Path


# =============================================================================
# CORES ANSI
# =============================================================================
class Colors:
    """Cores ANSI para formatação de terminal."""
    RED = "\033[1;31m"
    GREEN = "\033[1;32m"
    CYAN = "\033[1;36m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[1;34m"
    MAGENTA = "\033[1;35m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


# Atalhos para cores
re = Colors.RED
gr = Colors.GREEN
cy = Colors.CYAN
ye = Colors.YELLOW
bl = Colors.BLUE
ma = Colors.MAGENTA


# =============================================================================
# FUNÇÕES DE TERMINAL
# =============================================================================
def clear_screen() -> None:
    """Limpa a tela do terminal de forma cross-platform."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner(title: str = "Telegram Scraper", version: str = "3.1") -> None:
    """
    Exibe o banner do programa.
    
    Args:
        title: Título do programa
        version: Versão do programa
    """
    print(f"""
{re}╔╦╗{cy}┌─┐┬  ┌─┐{re}╔═╗  ╔═╗{cy}┌─┐┬─┐┌─┐┌─┐┌─┐┬─┐
{re} ║ {cy}├┤ │  ├┤ {re}║ ╦  ╚═╗{cy}│  ├┬┘├─┤├─┘├┤ ├┬╘
{re} ╩ {cy}└─┘┴─┘└─┘{re}╚═╝  ╚═╝{cy}└─┘┴└─┴ ┴┴  └─┘┴└─

            version : {version}
        """)


def print_error(message: str) -> None:
    """Imprime mensagem de erro."""
    print(f"{re}[!] {message}{Colors.RESET}")


def print_success(message: str) -> None:
    """Imprime mensagem de sucesso."""
    print(f"{gr}[+] {message}{Colors.RESET}")


def print_info(message: str) -> None:
    """Imprime mensagem informativa."""
    print(f"{cy}[*] {message}{Colors.RESET}")


def print_warning(message: str) -> None:
    """Imprime mensagem de aviso."""
    print(f"{ye}[!] {message}{Colors.RESET}")


def get_input(prompt: str, default: Optional[str] = None) -> str:
    """
    Obtém entrada do usuário com cor.
    
    Args:
        prompt: Mensagem do prompt
        default: Valor padrão se nenhuma entrada
        
    Returns:
        Entrada do usuário ou valor padrão
    """
    full_prompt = f"{gr}{prompt}{re}"
    if default:
        user_input = input(full_prompt)
        return user_input if user_input else default
    return input(full_prompt)


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================
CONFIG_FILE = 'config.data'


def get_config_path() -> Path:
    """Retorna o caminho do arquivo de configuração."""
    return Path(CONFIG_FILE)


def config_exists() -> bool:
    """Verifica se o arquivo de configuração existe."""
    return get_config_path().exists()


def load_credentials() -> Tuple[str, str, str]:
    """
    Carrega credenciais do arquivo de configuração.
    
    Returns:
        Tupla com (api_id, api_hash, phone)
        
    Raises:
        FileNotFoundError: Se config.data não existir
        KeyError: Se credenciais estiverem incompletas
    """
    if not config_exists():
        raise FileNotFoundError(f"{CONFIG_FILE} não encontrado. Execute: python3 setup.py -c")
    
    cpass = configparser.RawConfigParser()
    cpass.read(CONFIG_FILE)
    
    try:
        api_id = cpass['cred']['id']
        api_hash = cpass['cred']['hash']
        phone = cpass['cred']['phone']
        return api_id, api_hash, phone
    except KeyError as e:
        raise KeyError(f"Credencial ausente no config: {e}")


def save_credentials(api_id: str, api_hash: str, phone: str) -> None:
    """
    Salva credenciais no arquivo de configuração.
    
    Args:
        api_id: API ID do Telegram
        api_hash: API Hash do Telegram
        phone: Número de telefone
    """
    cpass = configparser.RawConfigParser()
    cpass.add_section('cred')
    cpass.set('cred', 'id', api_id)
    cpass.set('cred', 'hash', api_hash)
    cpass.set('cred', 'phone', phone)
    
    with open(CONFIG_FILE, 'w') as f:
        cpass.write(f)
    
    print_success(f"Credenciais salvas em {CONFIG_FILE}")


# =============================================================================
# TELEGRAM CLIENT
# =============================================================================
def create_telegram_client(phone: Optional[str] = None, api_id: Optional[str] = None, 
                          api_hash: Optional[str] = None):
    """
    Cria e retorna um cliente Telegram.
    
    Args:
        phone: Número de telefone (opcional se credentials existirem)
        api_id: API ID (opcional)
        api_hash: API Hash (opcional)
        
    Returns:
        TelegramClient conectado
        
    Raises:
        FileNotFoundError: Se credenciais não forem fornecidas
    """
    from telethon.sync import TelegramClient
    
    # Se não forneceu credenciais, tenta carregar do config
    if not all([phone, api_id, api_hash]):
        try:
            api_id, api_hash, phone = load_credentials()
        except (FileNotFoundError, KeyError) as e:
            print_error(str(e))
            sys.exit(1)
    
    client = TelegramClient(phone, api_id, api_hash)
    client.connect()
    
    if not client.is_user_authorized():
        client.send_code_request(phone)
        clear_screen()
        print_banner()
        code = get_input('[+] Enter the code: ')
        client.sign_in(phone, code)
    
    return client


# =============================================================================
# UTILITÁRIOS DE ARQUIVO
# =============================================================================
def ensure_csv_encoding(filepath: str, encoding: str = 'UTF-8'):
    """
    Garante que o arquivo CSV pode ser lido com a codificação especificada.
    
    Args:
        filepath: Caminho do arquivo CSV
        encoding: Codificação a ser usada
        
    Returns:
        Lista de dicionários com dados do CSV
    """
    import csv
    
    users = []
    with open(filepath, encoding=encoding) as f:
        rows = csv.reader(f, delimiter=",", lineterminator="\n")
        next(rows, None)  # Pula cabeçalho
        for row in rows:
            if len(row) >= 4:
                user = {
                    'username': row[0],
                    'id': int(row[1]) if row[1] else 0,
                    'access_hash': int(row[2]) if row[2] else 0,
                    'name': row[3]
                }
                users.append(user)
    return users


def save_to_csv(filepath: str, data: list, headers: list) -> None:
    """
    Salva dados em arquivo CSV.
    
    Args:
        filepath: Caminho do arquivo
        data: Lista de dicionários com dados
        headers: Lista de nomes das colunas
    """
    import csv
    
    with open(filepath, "w", encoding='UTF-8') as f:
        writer = csv.writer(f, delimiter=",", lineterminator="\n")
        writer.writerow(headers)
        for item in data:
            writer.writerow(item)
    
    print_success(f"Dados salvos em {filepath}")


# =============================================================================
# VALIDAÇÃO
# =============================================================================
def validate_positive_integer(value: str, name: str = "valor") -> int:
    """
    Valida que um valor é um inteiro positivo.
    
    Args:
        value: String a ser validada
        name: Nome do campo para mensagem de erro
        
    Returns:
        Inteiro validado
        
    Raises:
        ValueError: Se não for um inteiro positivo
    """
    try:
        num = int(value)
        if num < 0:
            raise ValueError(f"{name} deve ser positivo")
        return num
    except ValueError as e:
        raise ValueError(f"Invalid {name}: {e}")


def select_from_list(items: list, prompt: str = "Escolha uma opção") -> int:
    """
    Permite selecionar um item de uma lista numerada.
    
    Args:
        items: Lista de itens
        prompt: Mensagem do prompt
        
    Returns:
        Índice do item selecionado
        
    Raises:
        ValueError: Se a seleção for inválida
    """
    print(f"{gr}{prompt}:{re}")
    for i, item in enumerate(items):
        print(f"{gr}[{cy}{i}{gr}]{cy} - {item}")
    
    selection = input(f"\n{gr}[+] Número: {re}")
    try:
        index = int(selection)
        if 0 <= index < len(items):
            return index
        raise ValueError("Fora do intervalo")
    except ValueError:
        raise ValueError("Seleção inválida")


# =============================================================================
# RATE LIMITING
# =============================================================================
import time
import random


class RateLimiter:
    """Gerenciador de rate limiting para evitar bloqueios."""
    
    def __init__(self, min_delay: int = 5, max_delay: int = 10):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.consecutive_errors = 0
    
    def wait(self) -> None:
        """Aguarda um tempo aleatório entre requisições."""
        delay = random.uniform(self.min_delay, self.max_delay)
        time.sleep(delay)
    
    def on_error(self) -> None:
        """Aumenta o delay após um erro."""
        self.consecutive_errors += 1
        delay = min(self.min_delay * (2 ** self.consecutive_errors), 300)
        print_warning(f"Erro detectado. Aguardando {delay:.1f}s...")
        time.sleep(delay)
    
    def on_success(self) -> None:
        """Reseta o contador de erros após sucesso."""
        self.consecutive_errors = 0
