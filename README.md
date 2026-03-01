<p align="center">
  <img src="https://raw.githubusercontent.com/th3unkn0n/TeleGram-Scraper/master/.image/20191203_205322.jpg" width="470" height="150">
</p>

<p align="center"><img src="https://img.shields.io/badge/Version-3.1-brightgreen"></p>
<p align="center">
  Telegram Group Scraper
</p>

---

## • Configuração da API

1. Acesse [my.telegram.org](http://my.telegram.org) e faça login
2. Clique em API development tools e preencha os campos necessários
3. Defina o nome do app e selecione a plataforma
4. Copie o "api_id" e "api_hash" após criar o app

## • Como Instalar e Usar

```bash
# Instalar dependências do sistema
$ pkg install -y git python

# Clonar o repositório
$ git clone <url-do-repositorio>

# Entrar no diretório
$ cd Telegram-Scraper

# Instalar dependências Python
$ pip3 install -r requirements.txt
# ou
$ python3 setup.py -i

# Configurar credenciais (api_id, api_hash)
$ python3 setup.py -c
```

## • Comandos

```bash
# Coletar membros de um grupo
$ python3 scraper.py

# Adicionar membros a um grupo
$ python3 add2group.py members.csv

# Enviar mensagens em massa
$ python3 smsbot.py members.csv

# Mesclar arquivos CSV
$ python3 setup.py -m arquivo1.csv arquivo2.csv

# Ver ajuda
$ python3 setup.py -h
```

---

## • Requisitos

- Python 3.7+
- Telegram API ID e Hash
- Conta do Telegram

## • Notas

- O arquivo `members.csv` é gerado automaticamente pelo scraper
- Use com responsabilidade - respeite os Termos de Serviço do Telegram
- Mantenha suas credenciais em segurança
