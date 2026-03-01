#!/bin/env python3
"""
Telegram Group Member Adder
Adiciona membros de um CSV a um grupo do Telegram.

Uso: python3 add2group.py <arquivo.csv>
"""

from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
import sys
import time
import random
import traceback
from typing import List

# Módulo local
import utils
from utils import Colors, re, gr, cy, print_success, print_error, print_info, print_warning


def get_groups(client: TelegramClient) -> List:
    """
    Obtém lista de grupos do usuário.
    
    Args:
        client: Instância conectada do TelegramClient
        
    Returns:
        Lista de grupos (megagroups)
    """
    chats = []
    last_date = None
    chunk_size = 200
    
    result = client(GetDialogsRequest(
        offset_date=last_date,
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=chunk_size,
        hash=0
    ))
    chats.extend(result.chats)
    
    groups = []
    for chat in chats:
        try:
            if getattr(chat, 'megagroup', False):
                groups.append(chat)
        except AttributeError:
            continue
    
    return groups


def load_users_from_csv(filepath: str) -> List[dict]:
    """
    Carrega usuários de um arquivo CSV.
    
    Args:
        filepath: Caminho do arquivo CSV
        
    Returns:
        Lista de dicionários com dados dos usuários
    """
    return utils.ensure_csv_encoding(filepath)


def add_members(client: TelegramClient, target_group, users: List[dict], mode: int) -> None:
    """
    Adiciona membros ao grupo.
    
    Args:
        client: Instância do TelegramClient
        target_group: Grupo de destino
        users: Lista de usuários para adicionar
        mode: 1 = por username, 2 = por ID
    """
    from telethon.tl.functions.channels import InviteToChannelRequest
    
    target_entity = InputPeerChannel(target_group.id, target_group.access_hash)
    n = 0
    added = 0
    failed = 0
    
    for user in users:
        n += 1
        
        # Delay a cada 50 usuários
        if n % 50 == 0:
            time.sleep(1)
        
        try:
            print_info(f"Adicionando {user.get('name', user.get('username', 'Unknown'))}")
            
            if mode == 1:
                # Por username
                if not user.get('username'):
                    print_warning(f"Usuário sem username, pulando: {user.get('name')}")
                    failed += 1
                    continue
                user_to_add = client.get_input_entity(user['username'])
            elif mode == 2:
                # Por ID
                user_to_add = InputPeerUser(user['id'], user['access_hash'])
            else:
                print_error("Modo inválido!")
                return
            
            client(InviteToChannelRequest(target_entity, [user_to_add]))
            added += 1
            
            # Tempo aleatório entre adições
            delay = random.randrange(5, 10)
            print_success(f"Aguardando {delay}s...")
            time.sleep(delay)
            
        except PeerFloodError:
            print_error("Erro de flood do Telegram.")
            print_warning("Aguarde alguns minutos e tente novamente.")
            break
        except UserPrivacyRestrictedError:
            print_warning(f"Privacidade do usuário não permite: {user.get('name')}")
            failed += 1
            continue
        except Exception as e:
            print_error(f"Erro: {str(e)}")
            failed += 1
            continue
    
    # Resumo
    print_success(f"\n=== Resumo ===")
    print_info(f"Total processados: {n}")
    print_success(f"Adicionados: {added}")
    print_warning(f"Falhos: {failed}")


def main():
    """Função principal."""
    # Verificar argumento
    if len(sys.argv) < 2:
        print_error("Uso: python3 add2group.py <arquivo.csv>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # Banner
    utils.clear_screen()
    utils.print_banner(title="Add to Group")
    
    try:
        client = utils.create_telegram_client()
    except (FileNotFoundError, KeyError) as e:
        print_error(str(e))
        sys.exit(1)
    
    utils.clear_screen()
    utils.print_banner(title="Add to Group")
    
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
    
    # Obter grupos
    print_info("Carregando grupos...")
    groups = get_groups(client)
    
    if not groups:
        print_error("Nenhum grupo encontrado!")
        client.disconnect()
        sys.exit(1)
    
    # Seleção de grupo
    print_success("Escolha um grupo para adicionar membros:")
    for i, g in enumerate(groups):
        print(f"{gr}[{cy}{i}{gr}]{cy} - {g.title}")
    
    print()
    try:
        g_index = int(input(f"{gr}[+] Escolha um número: {re}"))
        if g_index < 0 or g_index >= len(groups):
            raise ValueError("Fora do intervalo")
    except ValueError:
        print_error("Seleção inválida!")
        client.disconnect()
        sys.exit(1)
    
    target_group = groups[g_index]
    
    # Seleção de modo
    print(f"\n{gr}[1]{cy} Adicionar por username")
    print(f"{gr}[2]{cy} Adicionar por ID")
    try:
        mode = int(input(f"\n{gr}[+] Modo: {re}"))
        if mode not in [1, 2]:
            raise ValueError("Modo inválido")
    except ValueError:
        print_error("Modo inválido!")
        client.disconnect()
        sys.exit(1)
    
    # Adicionar membros
    add_members(client, target_group, users, mode)
    
    client.disconnect()
    print_success("Operação concluída!")


if __name__ == "__main__":
    main()
