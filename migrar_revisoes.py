
#!/usr/bin/env python3
"""
Script para migrar dados de revisões do JSON para PostgreSQL
"""

from services.database import RevisaoService

def main():
    print("Iniciando migração de revisões...")
    
    revisao_service = RevisaoService()
    
    try:
        # Migra revisões
        if revisao_service.migrar_revisoes_json():
            print("✅ Revisões migradas com sucesso!")
        else:
            print("❌ Erro na migração das revisões")
    
    except Exception as e:
        print(f"❌ Erro na migração: {e}")

if __name__ == "__main__":
    main()
