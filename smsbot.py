#!/bin/env python3
"""
Telegram Bulk Message Sender
Envia mensagens em massa para usuários de um CSV.

Uso: python3 smsbot.py <arquivo.csv>
"""

from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerUser
from telethon.errors.rpcerrorlist import PeerFloodError
import sys
import time
from typing import List

# Módulo local
import utils
from utils import Colors, re, gr, cy, print_success, print_error, print_info, print_warning


# Tempo de espera entre mensagens (segundos)
DEFAULT_SLEEP_TIME = 30


def load_users_from_csv(filepath: str) -> List[dict]:
    """
    Carrega usuários de um arquivo CSV.
    
    Args:
        filepath: Caminho do arquivo CSV
        
    Returns:
        Lista de dicionários com dados dos usuários
    """
    return utils.ensure_csv_encoding(filepath)


def send_bulk_messages(client: TelegramClient, users: List[dict], 
                       message: str, mode: int) -> None:
    """
    Envia mensagens em massa para usuários.
    
    Args:
        client: Instância do TelegramClient
        users: Lista de usuários
        message: Mensagem a ser enviada
        mode: 1 = por ID, 2 = por username
    """
    sent = 0
    failed = 0
    
    for user in users:
        try:
            # Obter receptor
            if mode == 2:
                if not user.get('username'):
                    print_warning(f"Sem username: {user.get('name')}")
                    failed += 1
                    continue
                receiver = client.get_input_entity(user['username'])
            elif mode == 1:
                receiver = InputPeerUser(user['id'], user['access_hash'])
            else:
                print_error("Modo inválido!")
                return
            
            # Formatar mensagem com nome do usuário
            formatted_message = message.format(user.get('name', 'User'))
            
            print_info(f"Enviando para: {user.get('name', user.get('username', 'Unknown'))}")
            client.send_message(receiver, formatted_message)
            sent += 1
            
            print_success(f"Aguardando {DEFAULT_SLEEP_TIME}s...")
            time.sleep(DEFAULT_SLEEP_TIME)
            
        except PeerFloodError:
            print_error("Erro de flood do Telegram.")
            print_warning("Aguarde alguns minutos e tente novamente.")
            break
        except Exception as e:
            print_error(f"Erro com {user.get('name')}: {str(e)}")
            failed += 1
            continue
    
    # Resumo
    print_success(f"\n=== Resumo ===")
    print_info(f"Total processados: {len(users)}")
    print_success(f"Enviados: {sent}")
    print_warning(f"Falhos: {failed}")


def main():
    """Função principal."""
    # Verificar argumento
    if len(sys.argv) < 2:
        print_error("Uso: python3 smsbot.py <arquivo.csv>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # Banner
    utils.clear_screen()
    utils.print_banner(title="SMS Bot")
    
    try:
        client = utils.create_telegram_client()
    except (FileNotFoundError, KeyError) as e:
        print_error(str(e))
        sys.exit(1)
    
    utils.clear_screen()
    utils.print_banner(title="SMS Bot")
    
    # Carregar usuários
    try:
        users = load_users_from_csv(input_file)
        print_success(f"Carregados {len(users)} usuários de {input_file}")
    except FileNotFoundError:
        print_error(f"Arquivo não encontrado: {input_file}")
        client.disconnect()
        sys.exit(1)
    except Exception as e:
        print_error(f"Erro ao ler CSV: {e}")
        client.disconnect()
        sys.exit(1)
    
    # Seleção de modo
    print(f"{gr}[1]{cy} Enviar por ID")
    print(f"{gr}[2]{cy} Enviar por username")
    try:
        mode = int(input(f"\n{gr}[+] Modo: {re}"))
        if mode not in [1, 2]:
            raise ValueError("Modo inválido")
    except ValueError:
        print_error("Modo inválido!")
        client.disconnect()
        sys.exit(1)
    
    # Mensagem
    message = input(f"\n{gr}[+] Digite sua mensagem: {re}")
    print(f"\n{cy}Dica: Use {{name}} para incluir o nome do usuário{re}")
    
    # Confirmar
    confirm = input(f"\n{gr}[+] Confirmar envio? (s/n): {re}").lower()
    if confirm != 's':
        print_info("Operação cancelada.")
        client.disconnect()
        return
    
    # Enviar mensagens
    send_bulk_messages(client, users, message, mode)
    
    client.disconnect()
    print_success("Operação concluída!")


if __name__ == "__main__":
    main()
