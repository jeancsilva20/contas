
import hashlib
import json
from datetime import datetime

def gerar_hash_transacao(data, descricao, valor, tipo):
    """
    Gera um hash único para uma transação baseado em seus campos principais
    """
    # Converte a data para string se for datetime
    if isinstance(data, datetime):
        data_str = data.strftime('%Y-%m-%d')
    else:
        data_str = str(data)
    
    # Cria string combinada para hash
    combined = f"{data_str}_{descricao}_{valor}_{tipo}"
    
    # Gera hash SHA256
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()

def transacao_existe(hash_transacao, arquivo_transacoes='data/transacoes.json'):
    """
    Verifica se uma transação com o hash especificado já existe
    """
    try:
        with open(arquivo_transacoes, 'r', encoding='utf-8') as f:
            transacoes = json.load(f)
            return any(t.get('hash') == hash_transacao for t in transacoes)
    except FileNotFoundError:
        return False
    except json.JSONDecodeError:
        return False
