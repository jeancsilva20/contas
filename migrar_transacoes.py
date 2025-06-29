
#!/usr/bin/env python3
"""
Script para migrar dados de transações do JSON para PostgreSQL
"""

from services.database import TransacaoService

def main():
    print("Iniciando migração de transações...")
    
    transacao_service = TransacaoService()
    
    try:
        # Migra transações
        if transacao_service.migrar_transacoes_json():
            print("✅ Transações migradas com sucesso!")
            
            # Lista as transações migradas
            transacoes = transacao_service.listar_transacoes()
            print(f"\n📋 Transações migradas ({len(transacoes)}):")
            for transacao in transacoes[:5]:  # Mostra apenas as primeiras 5
                sinal = "+" if transacao['tipo_movimento'] == 'entrada' else ""
                print(f"  - {transacao['data']} | {transacao['descricao'][:50]}... | {sinal}R$ {transacao['valor']} | {transacao['fonte']}")
            
            if len(transacoes) > 5:
                print(f"  ... e mais {len(transacoes) - 5} transações")
        else:
            print("❌ Erro na migração das transações")
    
    except Exception as e:
        print(f"❌ Erro na migração: {e}")

if __name__ == "__main__":
    main()
