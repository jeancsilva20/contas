
#!/usr/bin/env python3
"""
Script para limpar todas as tabelas e migrar todos os dados dos arquivos JSON
"""

import os
import json
from services.database import DatabaseService

def carregar_dados_json():
    """Carrega todos os dados dos arquivos JSON"""
    dados = {}
    
    arquivos = {
        'fontes': 'data/fontes.json',
        'pendentes': 'data/pendentes.json', 
        'revisoes': 'data/revisoes.json',
        'transacoes': 'data/transacoes.json'
    }
    
    for nome, caminho in arquivos.items():
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                dados[nome] = json.load(f)
            print(f"✅ {nome}: {len(dados[nome])} registros carregados")
        except Exception as e:
            print(f"❌ Erro ao carregar {nome}: {e}")
            dados[nome] = []
    
    return dados

def executar_migracoes_sql(dados):
    """Executa as migrações SQL usando os dados carregados"""
    db = DatabaseService()
    
    try:
        print("\n🧹 Limpando tabelas...")
        
        # 1. Limpar tabelas na ordem correta
        queries_limpeza = [
            "TRUNCATE TABLE revisoes CASCADE;",
            "TRUNCATE TABLE pendentes CASCADE;", 
            "TRUNCATE TABLE transacoes CASCADE;",
            "TRUNCATE TABLE fontes CASCADE;"
        ]
        
        for query in queries_limpeza:
            db.execute_query(query)
        
        # 2. Resetar sequences
        sequences = [
            "ALTER SEQUENCE fontes_id_seq RESTART WITH 1;",
            "ALTER SEQUENCE transacoes_id_seq RESTART WITH 1;",
            "ALTER SEQUENCE pendentes_id_seq RESTART WITH 1;", 
            "ALTER SEQUENCE revisoes_id_seq RESTART WITH 1;"
        ]
        
        for seq in sequences:
            db.execute_query(seq)
        
        print("✅ Tabelas limpas e sequences resetadas")
        
        # 3. Inserir fontes
        print("\n📂 Inserindo fontes...")
        for fonte in dados['fontes']:
            query = "INSERT INTO fontes (nome, ativo, data_criacao) VALUES (%s, TRUE, CURRENT_TIMESTAMP)"
            db.execute_query(query, (fonte,))
        print(f"✅ {len(dados['fontes'])} fontes inseridas")
        
        # 4. Inserir transações
        print("\n💰 Inserindo transações...")
        for transacao in dados['transacoes']:
            query = """
            INSERT INTO transacoes (transacao_id, tipo, data, descricao, valor, tipo_movimento, fonte, hash, observacoes, ativo) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
            ON CONFLICT (hash) DO NOTHING
            """
            db.execute_query(query, (
                transacao.get('id'),
                transacao.get('tipo'),
                transacao.get('data'),
                transacao.get('descricao'),
                transacao.get('valor'),
                transacao.get('tipo_movimento'),
                transacao.get('fonte'),
                transacao.get('hash'),
                transacao.get('observacoes', '')
            ))
        print(f"✅ {len(dados['transacoes'])} transações inseridas")
        
        # 5. Inserir pendentes
        print("\n⏳ Inserindo pendentes...")
        for pendente in dados['pendentes']:
            query = """
            INSERT INTO pendentes (transacao_id, tipo, data, descricao, valor, tipo_movimento, fonte, hash, observacoes, ativo) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
            ON CONFLICT (hash) DO NOTHING
            """
            db.execute_query(query, (
                pendente.get('id'),
                pendente.get('tipo'),
                pendente.get('data'),
                pendente.get('descricao'),
                pendente.get('valor'),
                pendente.get('tipo_movimento'),
                pendente.get('fonte'),
                pendente.get('hash'),
                pendente.get('observacoes', '')
            ))
        print(f"✅ {len(dados['pendentes'])} pendentes inseridos")
        
        # 6. Inserir revisões
        print("\n📝 Inserindo revisões...")
        for revisao in dados['revisoes']:
            from datetime import datetime
            data_revisao = datetime.fromisoformat(revisao.get('data_revisao').replace('Z', '+00:00'))
            
            query = """
            INSERT INTO revisoes (hash, id_original, nova_descricao, donos, comentarios, pago_por, quitado, quitacao_individual, data_revisao, revisado_por, ativo) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
            ON CONFLICT (hash) DO NOTHING
            """
            db.execute_query(query, (
                revisao.get('hash'),
                revisao.get('id_original'),
                revisao.get('nova_descricao'),
                json.dumps(revisao.get('donos')),
                revisao.get('comentarios', ''),
                revisao.get('pago_por', ''),
                revisao.get('quitado', False),
                json.dumps(revisao.get('quitacao_individual', {})),
                data_revisao,
                revisao.get('revisado_por', '')
            ))
        print(f"✅ {len(dados['revisoes'])} revisões inseridas")
        
        # 7. Verificar inserções
        print("\n📊 Verificando inserções...")
        verificacao = """
        SELECT 'FONTES' as tabela, COUNT(*) as total FROM fontes
        UNION ALL
        SELECT 'TRANSAÇÕES' as tabela, COUNT(*) as total FROM transacoes
        UNION ALL
        SELECT 'PENDENTES' as tabela, COUNT(*) as total FROM pendentes
        UNION ALL
        SELECT 'REVISÕES' as tabela, COUNT(*) as total FROM revisoes
        """
        resultados = db.execute_query(verificacao, fetch=True)
        
        for resultado in resultados:
            print(f"   {resultado['tabela']}: {resultado['total']} registros")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        return False

def main():
    print("🚀 Iniciando reset completo e migração de dados...")
    print("=" * 60)
    
    # Carregar dados dos JSONs
    dados = carregar_dados_json()
    
    # Executar migrações
    if executar_migracoes_sql(dados):
        print("\n" + "=" * 60)
        print("🎉 RESET E MIGRAÇÃO CONCLUÍDOS COM SUCESSO!")
        print("=" * 60)
        print("\n💡 Todas as tabelas foram limpas e os dados dos arquivos JSON foram inseridos")
        print("   respeitando os relacionamentos entre as tabelas.")
    else:
        print("\n❌ Falha na migração!")

if __name__ == "__main__":
    main()
