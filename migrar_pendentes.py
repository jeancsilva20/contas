
#!/usr/bin/env python3
"""
Script para migrar dados de pendentes do arquivo JSON para PostgreSQL
"""

from services.database import PendenteService

def main():
    print("Iniciando migração de pendentes...")
    
    try:
        pendente_service = PendenteService()
        
        # Executa a migração
        if pendente_service.migrar_pendentes_json():
            print("✅ Migração concluída com sucesso!")
            
            # Lista os pendentes migrados
            pendentes = pendente_service.listar_pendentes()
            print(f"\n📋 Pendentes migrados ({len(pendentes)}):")
            for pendente in pendentes[:5]:  # Mostra apenas os primeiros 5
                print(f"  - {pendente['data']} | {pendente['descricao'][:50]}... | R$ {pendente['valor']}")
            
            if len(pendentes) > 5:
                print(f"  ... e mais {len(pendentes) - 5} pendentes")
        else:
            print("❌ Erro na migração!")
            
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")

if __name__ == "__main__":
    main()
