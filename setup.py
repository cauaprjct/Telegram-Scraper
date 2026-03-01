#!/bin/env python3
"""
Telegram Scraper Setup
Script de configuração e instalação.

Uso:
    python3 setup.py -c      Configurar API
    python3 setup.py -i      Instalar dependências
    python3 setup.py -m arquivo1.csv arquivo2.csv  Mesclar CSVs
    python3 setup.py -u      Atualizar ferramenta
    python3 setup.py -h      Ajuda
"""

import os
import sys
import subprocess
from pathlib import Path

# Módulo local
import utils
from utils import Colors, re, gr, cy, ye, print_success, print_error, print_info, print_warning


def check_python_version() -> bool:
    """Verifica se a versão do Python é compatível."""
    if sys.version_info < (3, 7):
        print_error("Python 3.7+ é necessário!")
        return False
    return True


def banner():
    """Exibe o banner do setup."""
    utils.clear_screen()
    print(f"""
{re}╔═╗{cy}┌─┐┌┬┐┬ ┬┌─┐
{re}╚═╗{cy}├┤  │ │ │├─┘
{re}╚═╝{cy}└─┘ ┴ └─┘┴
    """)


def requirements():
    """Instala as dependências necessárias."""
    banner()
    print_info("Instalando dependências...")
    
    # Dependências principais
    main_deps = ['telethon', 'requests', 'configparser', 'pytz']
    
    # Instalação
    for dep in main_deps:
        try:
            print_info(f"Instalando {dep}...")
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', dep],
                check=True,
                capture_output=True
            )
            print_success(f"{dep} instalado!")
        except subprocess.CalledProcessError:
            print_warning(f"Já instalado ou erro: {dep}")
    
    # Criar arquivo de config
    Path('config.data').touch()
    print_success("Arquivo config.data criado!")


def config_setup():
    """Configura as credenciais da API."""
    banner()
    print_info("Configuração da API Telegram")
    print("=" * 40)
    
    try:
        api_id = input(f"{gr}[+] API ID: {re}")
        api_hash = input(f"{gr}[+] API Hash: {re}")
        phone = input(f"{gr}[+] Telefone (+5511999999999): {re}")
    except KeyboardInterrupt:
        print("\n")
        print_warning("Cancelado pelo usuário")
        return
    
    if not all([api_id, api_hash, phone]):
        print_error("Todos os campos são obrigatórios!")
        return
    
    # Salvar
    utils.save_credentials(api_id, api_hash, phone)
    print_success("\nConfiguração concluída!")


def merge_csv():
    """Mescla dois arquivos CSV."""
    banner()
    
    if len(sys.argv) < 4:
        print_error("Uso: python3 setup.py -m arquivo1.csv arquivo2.csv")
        return
    
    file1_path = sys.argv[2]
    file2_path = sys.argv[3]
    
    # Verificar arquivos
    if not Path(file1_path).exists():
        print_error(f"Arquivo não encontrado: {file1_path}")
        return
    
    if not Path(file2_path).exists():
        print_error(f"Arquivo não encontrado: {file2_path}")
        return
    
    print_info(f"Mesclando {file1_path} e {file2_path}...")
    
    try:
        import pandas as pd
        
        file1 = pd.read_csv(file1_path)
        file2 = pd.read_csv(file2_path)
        
        print_info("Isso pode levar alguns segundos...")
        merge = file1.merge(file2, on='username', how='outer')
        merge.to_csv("output.csv", index=False)
        
        print_success(f"Arquivo salvo como output.csv")
        print_info(f"Total de registros: {len(merge)}")
        
    except ImportError:
        print_error("pandas não está instalado!")
        print_info("Execute: pip3 install pandas numpy")
    except Exception as e:
        print_error(f"Erro ao mesclar: {e}")


def update_tool():
    """Atualiza a ferramenta para a versão mais recente."""
    banner()
    print_warning("Esta função requer conexão com a internet")
    
    try:
        import requests as r
        
        print_info("Verificando atualizações...")
        
        # Nota: Este é um exemplo - atualize a URL do seu fork/repositório
        print_warning("Funcionalidade de atualização desabilitada")
        print_info("Clone o repositório mais recente manualmente:")
        print("  git clone <seu-repositorio>")
        
    except Exception as e:
        print_error(f"Erro: {e}")


def show_help():
    """Exibe a ajuda."""
    banner()
    print("""
$ python3 setup.py -m file1.csv file2.csv

( --config  / -c ) Configurar API
( --merge   / -m ) Mesclar 2 arquivos CSV
( --update  / -u ) Atualizar ferramenta
( --install / -i ) Instalar dependências
( --help    / -h ) Mostrar esta ajuda
    """)


def main():
    """Função principal."""
    if not check_python_version():
        sys.exit(1)
    
    if len(sys.argv) < 2:
        banner()
        print(f"{re}[!] Nenhum argumento fornecido{cy}")
        print(f"{gr}[*] Para ajuda: python3 setup.py -h{re}")
        sys.exit(1)
    
    arg = sys.argv[1].lower()
    
    if arg in ['--config', '-c']:
        config_setup()
    elif arg in ['--merge', '-m']:
        merge_csv()
    elif arg in ['--update', '-u']:
        update_tool()
    elif arg in ['--install', '-i']:
        requirements()
    elif arg in ['--help', '-h']:
        show_help()
    else:
        banner()
        print(f"{re}[!] Argumento desconhecido: {arg}")
        print(f"{gr}[*] Para ajuda: python3 setup.py -h{re}")


if __name__ == "__main__":
    main()
