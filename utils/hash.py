
import hashlib
import json
from datetime import datetime

def gerar_hash_transacao(data, descricao, valor, tipo):
    """
    Gera um hash único para uma transação baseado em seus dados principais
    """
    if isinstance(data, str):
        data_str = data
    else:
        data_str = data.strftime('%Y-%m-%d')
    
    # String única baseada nos dados da transação
    transacao_str = f"{data_str}|{descricao}|{valor}|{tipo}"
    
    # Gera hash SHA-256
    hash_obj = hashlib.sha256(transacao_str.encode('utf-8'))
    return hash_obj.hexdigest()

def transacao_existe(hash_transacao):
    """
    Verifica se uma transação já existe no banco de dados pelo hash
    """
    try:
        from services.database import TransacaoService
        transacao_service = TransacaoService()
        return transacao_service.transacao_existe(hash_transacao)
    except Exception as e:
        print(f"Erro ao verificar existência da transação: {e}")
        return False

def revisao_existe(hash_transacao):
    """
    Verifica se uma revisão já existe no banco de dados pelo hash
    """
    try:
        from services.database import RevisaoService
        revisao_service = RevisaoService()
        return revisao_service.revisao_existe(hash_transacao)
    except Exception as e:
        print(f"Erro ao verificar existência da revisão: {e}")
        return False

def pendente_existe(hash_transacao):
    """
    Verifica se uma transação pendente já existe no banco de dados pelo hash
    """
    try:
        from services.database import PendenteService
        pendente_service = PendenteService()
        return pendente_service.pendente_existe(hash_transacao)
    except Exception as e:
        print(f"Erro ao verificar existência do pendente: {e}")
        return False
