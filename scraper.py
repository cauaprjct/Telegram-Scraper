#!/bin/env python3
"""
Telegram Group Scraper
Coleta membros de grupos do Telegram e salva em CSV.

Uso: python3 scraper.py
"""

from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, UserStatusRecently, UserStatusLastMonth
from telethon.tl.types import UserStatusLastWeek, UserStatusEmpty, UserStatusOffline
import csv
import time
from datetime import datetime
from typing import List, Optional
import sys

# Módulo local
import utils
from utils import Colors, re, gr, cy, print_success, print_error, print_info


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


def filter_by_lastseen(user, minutes: int) -> bool:
    """
    Verifica se o usuário está online nos últimos minutos.
    
    Args:
        user: Usuário do Telegram
        minutes: Minutos para verificação
        
    Returns:
        True se usuário está dentro do tempo especificado
    """
    import pytz
    
    # Usuários com status recente ou online
    if isinstance(user.status, (UserStatusRecently, UserStatusOffline)):
        try:
            if isinstance(user.status, UserStatusOffline):
                time_delta = datetime.now(pytz.utc) - user.status.was_online
                total_seconds = time_delta.total_seconds()
                minutes_online = total_seconds / 60
                return minutes_online <= minutes
            return True  # UserStatusRecently está ativo
        except Exception:
            return True
    
    # Usuários com status último mês/semana/vazio - filtrar
    if isinstance(user.status, (UserStatusLastMonth, UserStatusLastWeek, UserStatusEmpty)):
        return False
    
    return True if user.status is None else False


def get_user_data(user) -> dict:
    """
    Extrai dados do usuário para salvar no CSV.
    
    Args:
        user: Usuário do Telegram
        
    Returns:
        Dicionário com dados do usuário
    """
    username = user.username or ""
    first_name = user.first_name or ""
    last_name = user.last_name or ""
    name = f"{first_name} {last_name}".strip()
    
    return {
        'username': username,
        'user_id': user.id,
        'access_hash': user.access_hash,
        'name': name
    }


def save_members(participants: List, group_title: str, group_id: int, 
                filename: str = "members.csv") -> None:
    """
    Salva membros em arquivo CSV.
    
    Args:
        participants: Lista de participantes
        group_title: Título do grupo
        group_id: ID do grupo
        filename: Nome do arquivo de saída
    """
    with open(filename, "w", encoding='UTF-8') as f:
        writer = csv.writer(f, delimiter=",", lineterminator="\now(['username', 'user id',")
        writer.writer 'access hash', 'name', 'group', 'group id'])
        
        for user in participants:
            data = get_user_data(user)
            writer.writerow([
                data['username'],
                data['user_id'],
                data['access_hash'],
                data['name'],
                group_title,
                group_id
            ])
    
    print_success(f"Membros salvos em {filename}")


def main():
    """Função principal do scraper."""
    # Banner e inicialização
    utils.clear_screen()
    utils.print_banner()
    
    try:
        # Conexão com Telegram
        client = utils.create_telegram_client()
    except (FileNotFoundError, KeyError) as e:
        print_error(str(e))
        sys.exit(1)
    
    utils.clear_screen()
    utils.print_banner()
    
    # Obter grupos
    print_info("Carregando grupos...")
    groups = get_groups(client)
    
    if not groups:
        print_error("Nenhum grupo encontrado!")
        client.disconnect()
        sys.exit(1)
    
    # Seleção de grupo
    print_success("Escolha um grupo para coletar membros:")
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
    
    # Filtrar por last seen
    try:
        g_lastseen = int(input(f"{gr}[+] Minutos para last seen (0 = todos): {re}"))
    except ValueError:
        g_lastseen = 0
    
    print_info("Coletando membros...")
    time.sleep(1)
    
    # Obter participantes
    try:
        all_participants = client.get_participants(target_group, aggressive=True)
    except Exception as e:
        print_error(f"Erro ao coletar: {e}")
        client.disconnect()
        sys.exit(1)
    
    # Filtrar por last seen se especificado
    if g_lastseen > 0:
        filtered = [u for u in all_participants if filter_by_lastseen(u, g_lastseen)]
    else:
        filtered = all_participants
    
    print_success(f"Encontrados {len(filtered)} membros")
    print_info("Salvando em arquivo...")
    time.sleep(1)
    
    # Salvar
    save_members(filtered, target_group.title, target_group.id)
    
    client.disconnect()
    print_success("Coleta concluída com sucesso!")


if __name__ == "__main__":
    main()
